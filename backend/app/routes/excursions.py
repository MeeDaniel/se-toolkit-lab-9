from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models import Excursion
from app.schemas import ExcursionCreate, ExcursionResponse, ExcursionFromMessage, ExcursionResponseWithAI, ExcursionUpdate
from app.services.ai_service import ai_service

router = APIRouter()


@router.get("/", response_model=List[ExcursionResponse])
async def get_excursions(
    user_id: int,
    offset: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """Get excursions for a specific user with pagination"""
    result = await db.execute(
        select(Excursion)
        .where(Excursion.user_id == user_id)
        .order_by(Excursion.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    excursions = result.scalars().all()
    return excursions


@router.get("/{excursion_id}", response_model=ExcursionResponse)
async def get_excursion(
    excursion_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific excursion by ID for a user"""
    result = await db.execute(
        select(Excursion).where(
            Excursion.id == excursion_id,
            Excursion.user_id == user_id
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
):
    """Create a new excursion record for a user"""
    db_excursion = Excursion(**excursion.model_dump())
    db.add(db_excursion)
    await db.flush()
    await db.refresh(db_excursion)
    
    return db_excursion


@router.post("/from-message", response_model=ExcursionResponseWithAI)
async def create_excursion_from_message(
    data: ExcursionFromMessage,
    db: AsyncSession = Depends(get_db),
):
    """Create excursion(s) AND generate AI response in a single API call.
    Also handles UPDATE requests for existing excursions.
    This reduces response time from ~15s to ~5-10s by combining extraction + response.
    """
    # Single API call extracts data, detects updates, AND generates response
    batch, ai_response, update_data = await ai_service.extract_and_respond(data.message)
    
    # Handle UPDATE request if detected
    excursion_updated = False
    updated_excursion_id = None
    if update_data and "excursion_id" in update_data:
        excursion_id = update_data.pop("excursion_id")
        
        # Verify ownership
        result = await db.execute(
            select(Excursion).where(
                Excursion.id == excursion_id,
                Excursion.user_id == data.user_id
            )
        )
        excursion = result.scalar_one_or_none()
        
        if excursion:
            # Update only provided fields
            for field, value in update_data.items():
                if hasattr(excursion, field) and value is not None:
                    setattr(excursion, field, value)
            
            await db.flush()
            await db.refresh(excursion)
            excursion_updated = True
            updated_excursion_id = excursion_id
    
    # Save each new excursion separately
    created = []
    for extracted in batch.excursions:
        db_excursion = Excursion(
            user_id=data.user_id,
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
        updated_excursion_id=updated_excursion_id
    )


@router.put("/{excursion_id}", response_model=ExcursionResponse)
async def update_excursion(
    excursion_id: int,
    user_id: int,
    update_data: ExcursionUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an excursion's data"""
    result = await db.execute(
        select(Excursion).where(
            Excursion.id == excursion_id,
            Excursion.user_id == user_id
        )
    )
    excursion = result.scalar_one_or_none()
    
    if not excursion:
        raise HTTPException(status_code=404, detail="Excursion not found")
    
    # Update only provided fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(excursion, field, value)
    
    await db.flush()
    await db.refresh(excursion)
    
    return excursion


@router.delete("/{excursion_id}")
async def delete_excursion(
    excursion_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete an excursion"""
    result = await db.execute(
        select(Excursion).where(
            Excursion.id == excursion_id,
            Excursion.user_id == user_id
        )
    )
    excursion = result.scalar_one_or_none()
    
    if not excursion:
        raise HTTPException(status_code=404, detail="Excursion not found")
    
    await db.delete(excursion)
    return {"message": "Excursion deleted successfully"}
