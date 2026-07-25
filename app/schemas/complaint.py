from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class ComplaintExtractRequest(BaseModel):
    """Raw input: either pasted text, or text already extracted from an uploaded file."""
    raw_text: str


class ComplaintBase(BaseModel):
    complaint_source: Optional[str] = None
    customer_name: Optional[str] = None
    product_name: Optional[str] = None
    product_strength_grade: Optional[str] = None
    batch_lot_number: Optional[str] = None
    manufacturing_date: Optional[date] = None
    expiry_date: Optional[date] = None
    quantity_affected: Optional[str] = None
    complaint_type: Optional[str] = None
    complaint_date: Optional[date] = None
    detailed_complaint_description: Optional[str] = None
    initial_severity: Optional[str] = None
    priority: Optional[str] = None


class ComplaintCreate(ComplaintBase):
    raw_source_text: Optional[str] = None


class ComplaintUpdate(ComplaintBase):
    pass


class ComplaintOut(ComplaintBase):
    id: str
    completeness_score: Optional[float] = None
    missing_fields: Optional[list[str]] = None
    risk_classification: Optional[str] = None
    risk_rationale: Optional[str] = None
    duplicate_of: Optional[str] = None
    duplicate_confidence: Optional[float] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    complaint_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str
