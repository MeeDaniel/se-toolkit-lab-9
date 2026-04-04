from fastapi import APIRouter, HTTPException
from app.schemas import ChatMessage, AIExcursionExtraction
from app.services import ai_service

router = APIRouter()


@router.post("/extract", response_model=AIExcursionExtraction)
async def extract_excursion_data(message: ChatMessage):
    """Extract excursion statistics from a natural language message"""
    result = await ai_service.extract_excursion_data(message.message)
    return result


@router.post("/analyze")
async def analyze_statistics(message: ChatMessage):
    """Analyze excursion statistics based on user query"""
    # This would typically query the database for context
    # For now, return a simple response
    result = await ai_service.analyze_statistics(
        query=message.message,
        context="You have excursion data available. Use the /api/statistics endpoint to get actual data."
    )
    return {"response": result}
