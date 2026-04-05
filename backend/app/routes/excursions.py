from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models import Excursion
from app.schemas import ExcursionCreate, ExcursionResponse, ExcursionFromMessage
from app.services import ai_service

router = APIRouter()


@router.get("/", response_model=List[ExcursionResponse])
async def get_excursions(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Get all excursions for a specific user"""
    result = await db.execute(
        select(Excursion)
        .where(Excursion.user_id == user_id)
        .order_by(Excursion.created_at.desc())
        .offset(skip)
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


@router.post("/from-message", response_model=ExcursionResponse)
async def create_excursion_from_message(
    data: ExcursionFromMessage,
    db: AsyncSession = Depends(get_db),
):
    """Create excursion by extracting data from natural language message"""
    # Use AI to extract data
    extracted = await ai_service.extract_excursion_data(data.message)
    
    # Create excursion record
    db_excursion = Excursion(
        user_id=data.user_id,
        number_of_tourists=extracted.number_of_tourists,
        average_age=extracted.average_age,
        age_distribution=extracted.age_distribution,
        vivacity_before=extracted.vivacity_before,
        vivacity_after=extracted.vivacity_after,
        interest_in_it=extracted.interest_in_it,
        interests_list=extracted.interests_list,
        raw_message=data.message,
    )
    
    db.add(db_excursion)
    await db.flush()
    await db.refresh(db_excursion)
    
    return db_excursion


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
