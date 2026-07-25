"""
LangGraph pipeline for the AI Complaint Intake Assistant.

Graph shape:

    START -> extract_fields -> completeness_check -> classify_risk -> finalize -> END

- extract_fields:       gemma2-9b-it. Pulls structured form fields out of raw complaint text.
- completeness_check:   llama-3.3-70b-versatile. Flags which required fields are missing/weak,
                         and produces a 0-100 completeness score (Bonus: Completeness Checker).
- classify_risk:        llama-3.3-70b-versatile. Classifies severity/risk with a rationale,
                         reasoning like a QMS reviewer would (Bonus: AI Risk Classification).
- finalize:              merges everything into the final structured payload returned to the API.

Each node only edits its own slice of state, so the graph is easy to extend with more
bonus nodes (e.g. duplicate_detection, capa_recommendation) without touching existing ones.
"""
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END

from app.services.groq_client import call_json
from app.config import settings

REQUIRED_FIELDS = [
    "complaint_source", "customer_name", "product_name", "product_strength_grade",
    "batch_lot_number", "manufacturing_date", "expiry_date", "quantity_affected",
    "complaint_type", "complaint_date", "detailed_complaint_description",
]


class ComplaintState(TypedDict, total=False):
    raw_text: str

    # extraction output
    complaint_source: Optional[str]
    customer_name: Optional[str]
    product_name: Optional[str]
    product_strength_grade: Optional[str]
    batch_lot_number: Optional[str]
    manufacturing_date: Optional[str]
    expiry_date: Optional[str]
    quantity_affected: Optional[str]
    complaint_type: Optional[str]
    complaint_date: Optional[str]
    detailed_complaint_description: Optional[str]

    # completeness checker output
    completeness_score: float
    missing_fields: list[str]

    # risk classification output
    initial_severity: str
    priority: str
    risk_classification: str
    risk_rationale: str


def extract_fields(state: ComplaintState) -> ComplaintState:
    system = (
        "You are a data-extraction engine for a pharmaceutical Quality Management System (QMS) "
        "customer complaint intake form. Extract structured fields from the raw complaint text "
        "(which may be an email, a letter, or free-form notes). "
        "Return ONLY a JSON object with these exact keys (use null when a value is truly absent, "
        "never invent data): complaint_source, customer_name, product_name, product_strength_grade, "
        "batch_lot_number, manufacturing_date (YYYY-MM-DD or null), expiry_date (YYYY-MM-DD or null), "
        "quantity_affected, complaint_type, complaint_date (YYYY-MM-DD or null), "
        "detailed_complaint_description."
    )
    result = call_json(system, state["raw_text"], model=settings.groq_extraction_model)
    for key in ComplaintState.__annotations__:
        if key in result:
            state[key] = result[key]
    return state


def completeness_check(state: ComplaintState) -> ComplaintState:
    system = (
        "You are a QMS reviewer checking whether a customer complaint record has enough "
        "information to proceed to investigation, per Good Manufacturing Practice expectations. "
        "Given the extracted fields as JSON, return ONLY a JSON object with keys: "
        "completeness_score (integer 0-100) and missing_fields (array of field names that are "
        "null, empty, or too vague to act on). Be strict: a description like 'product was bad' "
        "with no specifics counts as incomplete."
    )
    extracted = {k: state.get(k) for k in REQUIRED_FIELDS}
    result = call_json(system, str(extracted), model=settings.groq_reasoning_model)
    state["completeness_score"] = float(result.get("completeness_score", 0))
    state["missing_fields"] = result.get("missing_fields", [])
    return state


def classify_risk(state: ComplaintState) -> ComplaintState:
    system = (
        "You are a pharmaceutical QMS quality reviewer performing initial risk triage on a "
        "customer complaint for an API/FDF manufacturer. Given the extracted complaint fields "
        "as JSON, return ONLY a JSON object with keys: "
        "initial_severity (one of: Minor, Major, Critical), "
        "priority (one of: Low, Medium, High, Urgent), "
        "risk_classification (one of: Low, Medium, High, Critical) - your overall AI risk rating, "
        "risk_rationale (2-3 sentences explaining the rating, referencing patient safety, "
        "regulatory exposure, or batch scope where relevant)."
    )
    extracted = {k: state.get(k) for k in REQUIRED_FIELDS}
    result = call_json(system, str(extracted), model=settings.groq_reasoning_model)
    state["initial_severity"] = result.get("initial_severity", "Major")
    state["priority"] = result.get("priority", "Medium")
    state["risk_classification"] = result.get("risk_classification", "Medium")
    state["risk_rationale"] = result.get("risk_rationale", "")
    return state


def finalize(state: ComplaintState) -> ComplaintState:
    # Placeholder for any last-mile normalization; kept as its own node so future
    # bonus nodes (duplicate_detection, capa_recommendation) can slot in before it.
    return state


def build_graph():
    graph = StateGraph(ComplaintState)
    graph.add_node("extract_fields", extract_fields)
    graph.add_node("completeness_check", completeness_check)
    graph.add_node("classify_risk", classify_risk)
    graph.add_node("finalize", finalize)

    graph.add_edge(START, "extract_fields")
    graph.add_edge("extract_fields", "completeness_check")
    graph.add_edge("completeness_check", "classify_risk")
    graph.add_edge("classify_risk", "finalize")
    graph.add_edge("finalize", END)

    return graph.compile()


_compiled_graph = None


def run_intake_pipeline(raw_text: str) -> ComplaintState:
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph.invoke({"raw_text": raw_text})
