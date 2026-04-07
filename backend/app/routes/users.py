from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext

from app.database import get_db
from app.models import User
from app.schemas import UserRegister, UserResponse, UserLogin

router = APIRouter()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user with login and password"""
    # Normalize to lowercase
    normalized_login = user_data.login.lower()

    # Check if user already exists
    result = await db.execute(
        select(User).where(User.login == normalized_login)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=409, detail="Login already taken")

    # Create new user with hashed password and auth token
    db_user = User(
        login=normalized_login,
        password_hash=hash_password(user_data.password)
    )
    db_user.generate_token()
    db.add(db_user)
    await db.flush()
    await db.refresh(db_user)

    return UserResponse(
        id=db_user.id,
        login=db_user.login,
        auth_token=db_user.auth_token,
        created_at=db_user.created_at
    )


@router.post("/login", response_model=UserResponse)
async def login_user(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Login with username and password"""
    normalized_login = login_data.login.lower()

    result = await db.execute(
        select(User).where(User.login == normalized_login)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid login or password")

    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid login or password")

    # Generate new token on each login (invalidates old sessions)
    user.generate_token()
    await db.flush()

    return UserResponse(
        id=user.id,
        login=user.login,
        auth_token=user.auth_token,
        created_at=user.created_at
    )


@router.get("/{login}", response_model=UserResponse)
async def get_user(
    login: str,
    db: AsyncSession = Depends(get_db),
):
    """Get user by login"""
    normalized_login = login.lower()
    result = await db.execute(
        select(User).where(User.login == normalized_login)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        id=user.id,
        login=user.login,
        created_at=user.created_at
    )
