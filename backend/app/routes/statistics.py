from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from collections import Counter

from app.database import get_db
from app.models import Excursion
from app.schemas import StatisticsResponse

router = APIRouter()


@router.get("/", response_model=StatisticsResponse)
async def get_statistics(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get overall excursion statistics for a user"""
    result = await db.execute(
        select(Excursion).where(Excursion.user_id == user_id)
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
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get correlations between tourist demographics and interests"""
    result = await db.execute(
        select(Excursion).where(Excursion.user_id == user_id)
    )
    excursions = result.scalars().all()
    
    if len(excursions) < 2:
        return {"message": "Need at least 2 excursions to calculate correlations"}
    
    # Simple correlation analysis
    correlations = {
        "age_vs_interest_in_it": _calculate_correlation(
            [e.average_age for e in excursions],
            [e.interest_in_it for e in excursions]
        ),
        "vivacity_change_vs_interest": _calculate_correlation(
            [e.vivacity_after - e.vivacity_before for e in excursions],
            [e.interest_in_it for e in excursions]
        ),
    }
    
    return {
        "correlations": correlations,
        "insights": _generate_correlation_insights(correlations)
    }


def _calculate_correlation(x: list[float], y: list[float]) -> float:
    """Calculate Pearson correlation coefficient"""
    n = len(x)
    if n == 0:
        return 0.0
    
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    
    numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    denom_x = sum((xi - mean_x) ** 2 for xi in x) ** 0.5
    denom_y = sum((yi - mean_y) ** 2 for yi in y) ** 0.5
    
    if denom_x == 0 or denom_y == 0:
        return 0.0
    
    return numerator / (denom_x * denom_y)


def _generate_correlation_insights(correlations: dict) -> str:
    """Generate human-readable insights from correlations"""
    insights = []
    
    for key, value in correlations.items():
        strength = "strong" if abs(value) > 0.7 else "moderate" if abs(value) > 0.4 else "weak"
        direction = "positive" if value > 0 else "negative"
        insights.append(f"{strength} {direction} correlation ({value:.2f}) for {key}")
    
    return "\n".join(insights) if insights else "No significant correlations found"
