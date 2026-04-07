from fastapi import APIRouter, Depends, HTTPException
from app.schemas import ChatMessage, AIExcursionExtraction
from app.services import ai_service
from app.models import User
from app.auth import get_current_user

router = APIRouter()


@router.post("/extract", response_model=AIExcursionExtraction)
async def extract_excursion_data(
    data: ChatMessage,
    current_user: User = Depends(get_current_user),
):
    """Extract excursion statistics from a natural language message"""
    result = await ai_service.extract_excursion_data(data.message)
    return result
