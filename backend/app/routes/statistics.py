from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from collections import Counter

from app.database import get_db
from app.models import Excursion, User
from app.schemas import StatisticsResponse
from app.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=StatisticsResponse)
async def get_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get overall excursion statistics for the authenticated user"""
    result = await db.execute(
        select(Excursion).where(Excursion.user_id == current_user.id)
    )
    excursions = result.scalars().all()
    
    if not excursions:
        return StatisticsResponse(
            total_excursions=0,
            avg_tourists_per_excursion=0.0,
            avg_age_all=0.0,
            avg_vivacity_before=0.0,
            avg_vivacity_after=0.0,
            avg_interest_in_it=0.0,
            top_interests=[],
        )
    
    total = len(excursions)
    avg_tourists = sum(e.number_of_tourists for e in excursions) / total
    avg_age = sum(e.average_age for e in excursions) / total
    avg_vivacity_before = sum(e.vivacity_before for e in excursions) / total
    avg_vivacity_after = sum(e.vivacity_after for e in excursions) / total
    avg_interest = sum(e.interest_in_it for e in excursions) / total
    
    # Extract top interests
    all_interests = []
    for e in excursions:
        if e.interests_list:
            all_interests.extend(e.interests_list.lower().split())
    
    interest_counts = Counter(all_interests)
    top_interests = [interest for interest, count in interest_counts.most_common(10)]
    
    return StatisticsResponse(
        total_excursions=total,
        avg_tourists_per_excursion=avg_tourists,
        avg_age_all=avg_age,
        avg_vivacity_before=avg_vivacity_before,
        avg_vivacity_after=avg_vivacity_after,
        avg_interest_in_it=avg_interest,
        top_interests=top_interests,
    )


@router.get("/correlations")
async def get_correlations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get correlations between tourist demographics and interests.
    Analyzes all meaningful pairs and returns the most interesting ones.
    """
    result = await db.execute(
        select(Excursion).where(Excursion.user_id == current_user.id)
    )
    excursions = result.scalars().all()

    if len(excursions) < 3:
        return {
            "message": "Need at least 3 excursions to calculate meaningful correlations",
            "current_count": len(excursions)
        }

    # Define all meaningful correlation pairs with labels
    correlation_pairs = [
        # Core relationships
        ("age_vs_interest_in_it", "Age vs IT Interest", 
         lambda e: e.average_age, lambda e: e.interest_in_it,
         "Does tourist age correlate with interest in IT topics?"),
        
        ("vivacity_change", "Vivacity Change During Tour",
         lambda e: e.vivacity_after - e.vivacity_before, lambda e: 1.0,  # Just show avg change
         None),  # This is a mean, not correlation
        
        ("vivacity_boost_vs_it_interest", "Vivacity Boost vs IT Interest",
         lambda e: e.vivacity_after - e.vivacity_before, lambda e: e.interest_in_it,
         "Do IT-interested tourists gain more energy from tours?"),
        
        ("vivacity_boost_vs_age", "Vivacity Boost vs Age",
         lambda e: e.vivacity_after - e.vivacity_before, lambda e: e.average_age,
         "Do younger or older tourists gain more energy?"),
        
        ("vivacity_boost_vs_group_size", "Vivacity Boost vs Group Size",
         lambda e: e.vivacity_after - e.vivacity_before, lambda e: e.number_of_tourists,
         "Do larger groups experience more energy boost?"),
        
        ("it_interest_vs_group_size", "IT Interest vs Group Size",
         lambda e: e.interest_in_it, lambda e: e.number_of_tourists,
         "Do larger groups show more or less IT interest?"),
        
        ("it_interest_vs_age_diversity", "IT Interest vs Age Diversity",
         lambda e: e.interest_in_it, lambda e: e.age_distribution if e.age_distribution else 5.0,
         "Do diverse-age groups have different IT interests?"),
        
        ("group_size_vs_starting_energy", "Group Size vs Starting Energy",
         lambda e: e.number_of_tourists, lambda e: e.vivacity_before,
         "Do larger groups start with different energy levels?"),
        
        ("group_size_vs_ending_energy", "Group Size vs Ending Energy",
         lambda e: e.number_of_tourists, lambda e: e.vivacity_after,
         "Do larger groups end with different energy levels?"),
        
        ("age_vs_starting_energy", "Age vs Starting Energy",
         lambda e: e.average_age, lambda e: e.vivacity_before,
         "Do younger/older groups start with different energy?"),
        
        ("age_vs_ending_energy", "Age vs Ending Energy",
         lambda e: e.average_age, lambda e: e.vivacity_after,
         "Do younger/older groups end with different energy?"),
        
        ("starting_vs_ending_energy", "Starting vs Ending Energy",
         lambda e: e.vivacity_before, lambda e: e.vivacity_after,
         "Does starting energy predict ending energy?"),
    ]

    # Calculate all correlations
    correlations = []
    
    for pair_id, label, x_fn, y_fn, question in correlation_pairs:
        try:
            if question is None:
                # This is a mean calculation, not correlation
                values = [x_fn(e) for e in excursions]
                avg_value = sum(values) / len(values)
                correlations.append({
                    "id": pair_id,
                    "label": label,
                    "type": "average",
                    "value": avg_value,
                    "formatted_value": f"{avg_value:.2f}" if avg_value < 1 else f"{avg_value:.0f}",
                    "interpretation": _interpret_average(pair_id, avg_value),
                    "question": question
                })
            else:
                x_values = [x_fn(e) for e in excursions]
                y_values = [y_fn(e) for e in excursions]
                corr_value = _calculate_correlation(x_values, y_values)
                
                # Only include correlations with meaningful strength
                if abs(corr_value) >= 0.25:  # Minimum threshold
                    correlations.append({
                        "id": pair_id,
                        "label": label,
                        "type": "correlation",
                        "value": corr_value,
                        "strength": _get_strength_label(corr_value),
                        "direction": "positive" if corr_value > 0 else "negative",
                        "interpretation": _interpret_correlation(pair_id, corr_value),
                        "question": question
                    })
        except Exception as e:
            print(f"Error calculating {pair_id}: {e}")
            continue

    # Sort by absolute correlation value (most interesting first)
    correlations.sort(key=lambda x: abs(x.get("value", 0)), reverse=True)

    # Calculate some additional insights
    total_excursions = len(excursions)
    avg_group_size = sum(e.number_of_tourists for e in excursions) / total_excursions
    avg_vivacity_boost = sum(e.vivacity_after - e.vivacity_before for e in excursions) / total_excursions
    
    # Find best and worst performing excursions
    best_excursion = max(excursions, key=lambda e: e.vivacity_after - e.vivacity_before)
    worst_excursion = min(excursions, key=lambda e: e.vivacity_after - e.vivacity_before)

    return {
        "total_excursions_analyzed": total_excursions,
        "summary": {
            "avg_group_size": round(avg_group_size, 1),
            "avg_vivacity_boost": round(avg_vivacity_boost, 2),
            "best_excursion": {
                "id": best_excursion.id,
                "vivacity_boost": round(best_excursion.vivacity_after - best_excursion.vivacity_before, 2),
                "tourists": best_excursion.number_of_tourists
            },
            "worst_excursion": {
                "id": worst_excursion.id,
                "vivacity_boost": round(worst_excursion.vivacity_after - worst_excursion.vivacity_before, 2),
                "tourists": worst_excursion.number_of_tourists
            },
            "most_interesting_correlations": correlations[:5]  # Top 5
        },
        "all_correlations": correlations
    }


def _interpret_average(pair_id: str, value: float) -> str:
    """Generate human-readable interpretation for averages"""
    if pair_id == "vivacity_change":
        if value > 0.15:
            return f"🎉 Tours energize tourists! Average energy boost: +{value*100:.0f}%"
        elif value > 0:
            return f"✅ Slight energy increase: +{value*100:.0f}%"
        else:
            return f"⚠️ Tours drain energy slightly: {value*100:.0f}%"
    return f"Average: {value:.2f}"


def _interpret_correlation(pair_id: str, value: float) -> str:
    """Generate human-readable interpretation for correlations"""
    strength = _get_strength_label(value)
    direction = "positive" if value > 0 else "negative"
    
    interpretations = {
        "vivacity_boost_vs_it_interest": (
            f"IT-interested tourists gain {'more' if value > 0 else 'less'} energy (+{abs(value)*100:.0f}% correlation)"
            if strength != "weak" else "IT interest has little effect on energy change"
        ),
        "vivacity_boost_vs_age": (
            f"{'Younger' if value < 0 else 'Older'} tourists gain more energy"
            if strength != "weak" else "Age has little effect on energy boost"
        ),
        "vivacity_boost_vs_group_size": (
            f"{'Larger' if value > 0 else 'Smaller'} groups gain more energy"
            if strength != "weak" else "Group size has little effect on energy boost"
        ),
        "it_interest_vs_group_size": (
            f"{'Larger' if value > 0 else 'Smaller'} groups show {'more' if value > 0 else 'less'} IT interest"
            if strength != "weak" else "Group size doesn't affect IT interest"
        ),
        "starting_vs_ending_energy": (
            f"Starting energy {'strongly predicts' if abs(value) > 0.7 else 'somewhat predicts'} ending energy"
            if strength != "weak" else "Starting energy doesn't predict ending energy"
        ),
    }
    
    return interpretations.get(pair_id, f"{strength} {direction} correlation ({value:.2f})")


def _get_strength_label(value: float) -> str:
    """Get strength label for correlation value"""
    abs_val = abs(value)
    if abs_val >= 0.7:
        return "strong"
    elif abs_val >= 0.4:
        return "moderate"
    else:
        return "weak"


def _calculate_correlation(x: list[float], y: list[float]) -> float:
    """Calculate Pearson correlation coefficient"""
    n = len(x)
    if n < 3:  # Need minimum 3 points for meaningful correlation
        return 0.0

    mean_x = sum(x) / n
    mean_y = sum(y) / n

    numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    denom_x = sum((xi - mean_x) ** 2 for xi in x) ** 0.5
    denom_y = sum((yi - mean_y) ** 2 for yi in y) ** 0.5

    if denom_x == 0 or denom_y == 0:
        return 0.0

    return numerator / (denom_x * denom_y)
