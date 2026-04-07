from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    login: str = Field(..., min_length=3, max_length=100, description="Username/login")
    password: str = Field(..., min_length=4, description="Password")


class UserLogin(BaseModel):
    login: str
    password: str


class UserResponse(BaseModel):
    id: int
    login: str
    auth_token: str
    created_at: datetime

    class Config:
        from_attributes = True


class ExcursionCreate(BaseModel):
    number_of_tourists: int = Field(..., gt=0, description="Number of tourists")
    average_age: float = Field(..., gt=0, description="Average age of tourists")
    age_distribution: Optional[float] = Field(None, description="Age distribution (std deviation)")
    vivacity_before: float = Field(..., ge=0, le=1, description="Vivacity before (0-1)")
    vivacity_after: float = Field(..., ge=0, le=1, description="Vivacity after (0-1)")
    interest_in_it: float = Field(..., ge=0, le=1, description="Interest in IT (0-1)")
    interests_list: Optional[str] = Field(None, description="Space-separated keywords")
    raw_message: Optional[str] = Field(None, description="Original message")


class ExcursionUpdate(BaseModel):
    number_of_tourists: Optional[int] = Field(None, gt=0)
    average_age: Optional[float] = Field(None, gt=0)
    age_distribution: Optional[float] = None
    vivacity_before: Optional[float] = Field(None, ge=0, le=1)
    vivacity_after: Optional[float] = Field(None, ge=0, le=1)
    interest_in_it: Optional[float] = Field(None, ge=0, le=1)
    interests_list: Optional[str] = None


class ExcursionResponse(BaseModel):
    id: int
    user_id: int
    number_of_tourists: int
    average_age: float
    age_distribution: Optional[float]
    vivacity_before: float
    vivacity_after: float
    interest_in_it: float
    interests_list: Optional[str]
    raw_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ExcursionFromMessage(BaseModel):
    message: str = Field(..., description="Natural language message about excursion")


class ExcursionQuery(BaseModel):
    query: str = Field(..., description="Natural language query about excursions")


class ChatMessage(BaseModel):
    message: str = Field(..., description="User message")


class AIExcursionExtraction(BaseModel):
    number_of_tourists: Optional[int] = None
    average_age: Optional[float] = None
    age_distribution: Optional[float] = None
    vivacity_before: Optional[float] = None
    vivacity_after: Optional[float] = None
    interest_in_it: Optional[float] = None
    interests_list: Optional[str] = None
    confidence: float = Field(..., ge=0, le=1, description="Extraction confidence (0-1)")
    raw_message: Optional[str] = None


class ExcursionBatch(BaseModel):
    excursions: list[AIExcursionExtraction]
    raw_message: Optional[str] = None


class ExcursionResponseWithAI(BaseModel):
    excursions: list[ExcursionResponse]
    ai_response: str
    excursion_stored: bool
    excursion_updated: bool
    updated_excursion_id: Optional[int] = None
    excursion_deleted: bool = False
    delete_message: Optional[str] = None


class StatisticsResponse(BaseModel):
    total_excursions: int
    avg_tourists_per_excursion: float
    avg_age_all: float
    avg_vivacity_before: float
    avg_vivacity_after: float
    avg_interest_in_it: float
    top_interests: list[str]
    correlations: Optional[dict] = None
