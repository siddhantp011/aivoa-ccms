from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.complaint import Complaint
from app.schemas.complaint import (
    ComplaintExtractRequest, ComplaintOut, ComplaintUpdate,
)
from app.graph.pipeline import run_intake_pipeline
from app.services.file_extraction import extract_text_from_upload

router = APIRouter(prefix="/api/complaints", tags=["complaints"])


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


@router.post("/extract", response_model=ComplaintOut)
def extract_complaint(payload: ComplaintExtractRequest, db: Session = Depends(get_db)):
    """
    Runs the LangGraph intake pipeline (extraction -> completeness check ->
    risk classification) over pasted complaint text and persists the result.
    This powers the "AI Complaint Intake Assistant" panel in the reference UI.
    """
    if not payload.raw_text or not payload.raw_text.strip():
        raise HTTPException(400, "raw_text must not be empty")

    result = run_intake_pipeline(payload.raw_text)

    complaint = Complaint(
        complaint_source=result.get("complaint_source"),
        customer_name=result.get("customer_name"),
        product_name=result.get("product_name"),
        product_strength_grade=result.get("product_strength_grade"),
        batch_lot_number=result.get("batch_lot_number"),
        manufacturing_date=_parse_date(result.get("manufacturing_date")),
        expiry_date=_parse_date(result.get("expiry_date")),
        quantity_affected=result.get("quantity_affected"),
        complaint_type=result.get("complaint_type"),
        complaint_date=_parse_date(result.get("complaint_date")),
        detailed_complaint_description=result.get("detailed_complaint_description"),
        initial_severity=result.get("initial_severity"),
        priority=result.get("priority"),
        completeness_score=result.get("completeness_score"),
        missing_fields=result.get("missing_fields"),
        risk_classification=result.get("risk_classification"),
        risk_rationale=result.get("risk_rationale"),
        raw_source_text=payload.raw_text,
        status="Pending Triage",
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


@router.post("/extract-file", response_model=ComplaintOut)
async def extract_complaint_from_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Same as /extract but takes an uploaded PDF/DOCX/TXT/EML file directly."""
    raw_text = await extract_text_from_upload(file)
    return extract_complaint(ComplaintExtractRequest(raw_text=raw_text), db)


@router.get("", response_model=list[ComplaintOut])
def list_complaints(db: Session = Depends(get_db)):
    return db.query(Complaint).order_by(Complaint.created_at.desc()).all()


@router.get("/{complaint_id}", response_model=ComplaintOut)
def get_complaint(complaint_id: str, db: Session = Depends(get_db)):
    complaint = db.get(Complaint, complaint_id)
    if not complaint:
        raise HTTPException(404, "Complaint not found")
    return complaint


@router.put("/{complaint_id}", response_model=ComplaintOut)
def update_complaint(complaint_id: str, payload: ComplaintUpdate, db: Session = Depends(get_db)):
    """Manual edits from the form (user overriding AI-extracted values) land here."""
    complaint = db.get(Complaint, complaint_id)
    if not complaint:
        raise HTTPException(404, "Complaint not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(complaint, field, value)
    complaint.status = "Saved"
    db.commit()
    db.refresh(complaint)
    return complaint


@router.delete("/{complaint_id}")
def delete_complaint(complaint_id: str, db: Session = Depends(get_db)):
    complaint = db.get(Complaint, complaint_id)
    if not complaint:
        raise HTTPException(404, "Complaint not found")
    db.delete(complaint)
    db.commit()
    return {"deleted": complaint_id}
