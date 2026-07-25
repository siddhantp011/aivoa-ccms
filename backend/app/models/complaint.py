import uuid
from datetime import datetime, date

from sqlalchemy import Column, String, Text, Date, DateTime, Float, JSON
from app.database import Base


def gen_id() -> str:
    return str(uuid.uuid4())


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(String(36), primary_key=True, default=gen_id)

    # 1. Origin & customer details
    complaint_source = Column(String(120))
    customer_name = Column(String(200))

    # 2. Product & batch identification
    product_name = Column(String(200))
    product_strength_grade = Column(String(120))
    batch_lot_number = Column(String(120))
    manufacturing_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    quantity_affected = Column(String(50))  # kept as string to hold "12 kg" style values

    # 3. Complaint details
    complaint_type = Column(String(120))
    complaint_date = Column(Date, nullable=True)
    detailed_complaint_description = Column(Text)

    # 4. Initial assessment & priority
    initial_severity = Column(String(50))
    priority = Column(String(50))

    # AI-derived metadata (populated by the LangGraph pipeline)
    completeness_score = Column(Float, nullable=True)       # 0-100
    missing_fields = Column(JSON, nullable=True)            # list[str]
    risk_classification = Column(String(50), nullable=True)  # Low / Medium / High / Critical
    risk_rationale = Column(Text, nullable=True)
    duplicate_of = Column(String(36), nullable=True)        # complaint id if flagged as duplicate
    duplicate_confidence = Column(Float, nullable=True)

    raw_source_text = Column(Text, nullable=True)  # original pasted/extracted text, for audit + chat

    status = Column(String(50), default="Pending Triage")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
