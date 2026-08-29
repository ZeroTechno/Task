from enum import Enum
from pydantic import BaseModel, Field


class CategoryEnum(str, Enum):
    BILLING = "billing"
    BUG = "bug"
    FEATURE = "feature"
    OTHER = "other"


class UrgencyEnum(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class TriageRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000, description="Support message text between 1 and 2000 chars")


class TriageResponse(BaseModel):
    category: CategoryEnum
    urgency: UrgencyEnum
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    reason: str = Field(..., max_length=200, description="Short one-sentence explanation")
