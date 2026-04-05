from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse

router = APIRouter()


@router.post("/", response_model=UserResponse)
async def create_or_get_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new user or return existing one"""
    result = await db.execute(
        select(User).where(User.telegram_alias == user_data.telegram_alias)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        return existing_user
    
    db_user = User(telegram_alias=user_data.telegram_alias)
    db.add(db_user)
    await db.flush()
    await db.refresh(db_user)
    
    return db_user


@router.get("/{telegram_alias}", response_model=UserResponse)
async def get_user(
    telegram_alias: str,
    db: AsyncSession = Depends(get_db),
):
    """Get user by telegram alias"""
    result = await db.execute(
        select(User).where(User.telegram_alias == telegram_alias)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user
