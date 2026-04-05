from fastapi import APIRouter, HTTPException
from app.schemas import ChatMessage, AIExcursionExtraction
from app.services import ai_service

router = APIRouter()


@router.post("/extract", response_model=AIExcursionExtraction)
async def extract_excursion_data(data: ChatMessage):
    """Extract excursion statistics from a natural language message"""
    result = await ai_service.extract_excursion_data(data.message)
    return result
