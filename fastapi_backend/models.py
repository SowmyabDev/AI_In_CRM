"""Request and response models with validation for the chatbot API."""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict
from datetime import datetime


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: str = Field(..., min_length=1, max_length=100)
    
    @validator('message')
    def message_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()


class LoginRequest(BaseModel):
    """Request model for login endpoint."""
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=100)
    session_id: str = Field(..., min_length=1, max_length=100)


class AddToCartRequest(BaseModel):
    """Request model for adding a product to cart."""
    product_id: int = Field(..., gt=0)
    session_id: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(default=1, gt=0)


class RemoveFromCartRequest(BaseModel):
    """Request model for removing a product from cart."""
    product_id: int = Field(..., gt=0)
    session_id: str = Field(..., min_length=1, max_length=100)


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    reply: str
    intent: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class LoginResponse(BaseModel):
    """Response model for login endpoint."""
    success: bool
    message: Optional[str] = None


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    ok: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"


class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str
    error_id: Optional[str] = None
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ProductResponse(BaseModel):
    """Response model for a product."""
    id: int
    name: str
    price: float
    description: Optional[str] = None
    category: Optional[str] = None
    rating: Optional[float] = None
    stock: Optional[int] = None


class AnalyticsResponse(BaseModel):
    """Response model for analytics metrics."""
    total_queries: int
    resolved_queries: int
    escalated_queries: int
    overall_resolution_rate: float
    overall_escalation_rate: float
    by_intent: Dict


class StaffingAnalysisResponse(BaseModel):
    """Response model for staffing analysis results."""
    chatbot_resolution_rate: float
    escalation_rate: float
    estimated_escalations_per_hour: float
    staffing_scenarios: List[Dict]
