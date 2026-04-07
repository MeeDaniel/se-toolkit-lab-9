from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import logging

from app.database import get_db
from app.models import Excursion, User
from app.schemas import ExcursionCreate, ExcursionResponse, ExcursionFromMessage, ExcursionResponseWithAI, ExcursionUpdate
from app.services.ai_service import ai_service
from app.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[ExcursionResponse])
async def get_excursions(
    offset: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get excursions for the authenticated user with pagination"""
    result = await db.execute(
        select(Excursion)
        .where(Excursion.user_id == current_user.id)
        .order_by(Excursion.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{excursion_id}", response_model=ExcursionResponse)
async def get_excursion(
    excursion_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific excursion by ID for the authenticated user"""
    result = await db.execute(
        select(Excursion).where(
            Excursion.id == excursion_id,
            Excursion.user_id == current_user.id
        )
    )
    excursion = result.scalar_one_or_none()

    if not excursion:
        raise HTTPException(status_code=404, detail="Excursion not found")

    return excursion


@router.post("/", response_model=ExcursionResponse)
async def create_excursion(
    excursion: ExcursionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new excursion record for the authenticated user"""
    db_excursion = Excursion(
        user_id=current_user.id,
        **excursion.model_dump()
    )
    db.add(db_excursion)
    await db.flush()
    await db.refresh(db_excursion)
    return db_excursion


@router.post("/from-message", response_model=ExcursionResponseWithAI)
async def create_excursion_from_message(
    data: ExcursionFromMessage,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create excursion(s) AND generate AI response in a single API call.
    Also handles UPDATE and DELETE requests for existing excursions.
    Fetches user's recent excursions to give AI context for update/delete operations.
    """
    # Fetch user's recent excursions (last 10) for AI context
    recent_result = await db.execute(
        select(Excursion)
        .where(Excursion.user_id == current_user.id)
        .order_by(Excursion.created_at.desc())
        .limit(10)
    )
    user_excursions = [
        {
            "id": e.id,
            "number_of_tourists": e.number_of_tourists,
            "average_age": e.average_age,
            "vivacity_before": e.vivacity_before,
            "vivacity_after": e.vivacity_after,
            "interest_in_it": e.interest_in_it,
            "interests_list": e.interests_list,
            "created_at": str(e.created_at) if e.created_at else "",
        }
        for e in recent_result.scalars().all()
    ]

    # Single API call with user's excursion context
    batch, ai_response, update_data, delete_data = await ai_service.extract_and_respond(
        data.message,
        user_excursions=user_excursions if user_excursions else None,
    )

    # Handle UPDATE request if detected
    excursion_updated = False
    updated_excursion_id = None
    if update_data and "excursion_id" in update_data:
        excursion_id_raw = update_data.pop("excursion_id")
        if not isinstance(excursion_id_raw, int):
            logger.warning(f"AI returned non-integer excursion_id for update: {excursion_id_raw!r}")
            ai_response += "\n\n⚠️ I couldn't identify a valid excursion to update."
        else:
            result = await db.execute(
                select(Excursion).where(
                    Excursion.id == excursion_id_raw,
                    Excursion.user_id == current_user.id
                )
            )
            excursion = result.scalar_one_or_none()

            if excursion:
                for field, value in update_data.items():
                    if hasattr(excursion, field) and value is not None:
                        setattr(excursion, field, value)
                await db.flush()
                await db.refresh(excursion)
                excursion_updated = True
                updated_excursion_id = excursion_id_raw
            else:
                logger.warning(f"User {current_user.id} tried to update non-owned excursion #{excursion_id_raw}")
                ai_response += f"\n\n⚠️ I couldn't find excursion #{excursion_id_raw} in your records."

    # Handle DELETE request if detected
    excursion_deleted = False
    delete_message = ""
    if delete_data and "excursion_id" in delete_data:
        excursion_id_raw = delete_data["excursion_id"]
        if not isinstance(excursion_id_raw, int):
            logger.warning(f"AI returned non-integer excursion_id for delete: {excursion_id_raw!r}")
            ai_response += "\n\n⚠️ I couldn't identify a valid excursion to delete."
        else:
            result = await db.execute(
                select(Excursion).where(
                    Excursion.id == excursion_id_raw,
                    Excursion.user_id == current_user.id
                )
            )
            excursion = result.scalar_one_or_none()

            if excursion:
                await db.delete(excursion)
                await db.flush()
                excursion_deleted = True
                delete_message = f"Excursion #{excursion_id_raw} has been deleted."
            else:
                logger.warning(f"User {current_user.id} tried to delete non-owned excursion #{excursion_id_raw}")
                ai_response += f"\n\n⚠️ I couldn't find excursion #{excursion_id_raw} in your records."

    # Save each new excursion
    created = []
    for extracted in batch.excursions:
        db_excursion = Excursion(
            user_id=current_user.id,
            number_of_tourists=extracted.number_of_tourists or 10,
            average_age=extracted.average_age or 25.0,
            age_distribution=extracted.age_distribution or 5.0,
            vivacity_before=extracted.vivacity_before or 0.5,
            vivacity_after=extracted.vivacity_after or 0.5,
            interest_in_it=extracted.interest_in_it or 0.5,
            interests_list=extracted.interests_list,
            raw_message=data.message,
        )
        db.add(db_excursion)
        await db.flush()
        await db.refresh(db_excursion)
        created.append(db_excursion)

    return ExcursionResponseWithAI(
        excursions=created,
        ai_response=ai_response,
        excursion_stored=len(created) > 0,
        excursion_updated=excursion_updated,
        updated_excursion_id=updated_excursion_id,
        excursion_deleted=excursion_deleted,
        delete_message=delete_message
    )


@router.put("/{excursion_id}", response_model=ExcursionResponse)
async def update_excursion(
    excursion_id: int,
    update_data: ExcursionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an excursion's data"""
    result = await db.execute(
        select(Excursion).where(
            Excursion.id == excursion_id,
            Excursion.user_id == current_user.id
        )
    )
    excursion = result.scalar_one_or_none()

    if not excursion:
        raise HTTPException(status_code=404, detail="Excursion not found")

    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(excursion, field, value)

    await db.flush()
    await db.refresh(excursion)
    return excursion


@router.delete("/{excursion_id}")
async def delete_excursion(
    excursion_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an excursion"""
    result = await db.execute(
        select(Excursion).where(
            Excursion.id == excursion_id,
            Excursion.user_id == current_user.id
        )
    )
    excursion = result.scalar_one_or_none()

    if not excursion:
        raise HTTPException(status_code=404, detail="Excursion not found")

    await db.delete(excursion)
    return {"message": "Excursion deleted successfully"}
