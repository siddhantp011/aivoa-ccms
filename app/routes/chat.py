from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.complaint import Complaint
from app.schemas.complaint import ChatRequest, ChatResponse
from app.services.groq_client import call_text
from app.config import settings

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    complaint = db.get(Complaint, payload.complaint_id)
    if not complaint:
        raise HTTPException(404, "Complaint not found")

    context = f"""
Complaint record (JSON-ish):
source={complaint.complaint_source}, customer={complaint.customer_name},
product={complaint.product_name} ({complaint.product_strength_grade}),
batch/lot={complaint.batch_lot_number}, mfg_date={complaint.manufacturing_date},
expiry={complaint.expiry_date}, qty_affected={complaint.quantity_affected},
type={complaint.complaint_type}, complaint_date={complaint.complaint_date},
description={complaint.detailed_complaint_description}
severity={complaint.initial_severity}, priority={complaint.priority}
completeness_score={complaint.completeness_score}, missing_fields={complaint.missing_fields}
risk_classification={complaint.risk_classification}, risk_rationale={complaint.risk_rationale}

Original raw source text:
{complaint.raw_source_text}
"""
    system = (
        "You are the AI Complaint Intake Assistant embedded in a pharmaceutical QMS "
        "customer complaint form. Answer the user's question about THIS specific complaint "
        "record only, using the context provided. Be concise and factual. If asked something "
        "the record doesn't cover, say so plainly rather than guessing."
    )
    reply = call_text(system, f"{context}\n\nUser question: {payload.message}", model=settings.groq_reasoning_model)
    return ChatResponse(reply=reply)
