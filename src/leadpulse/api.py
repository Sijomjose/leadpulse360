"""FastAPI REST application exposing LeadPulse 360 endpoints."""

from typing import Any, Dict

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from leadpulse.analytics import AnalyticsSummary
from leadpulse.audit import AuditLogger
from leadpulse.config import DEFAULT_CONFIG
from leadpulse.routing import RoutingDecision, determine_lead_route
from leadpulse.schemas import InboundLead
from leadpulse.scoring import ScoreResult, calculate_lead_score

app = FastAPI(
    title="LeadPulse 360 API",
    description="Automated Enterprise Lead Intake, Scoring & Decision Engine",
    version="1.0.0",
)

logger = AuditLogger()


class LeadTriageResponse(BaseModel):
    status: str
    lead_name: str
    work_email: str
    score: ScoreResult
    routing: RoutingDecision


@app.get("/health", tags=["System"])
def health_check() -> Dict[str, str]:
    """Basic health check probe for load balancers."""
    return {"status": "healthy", "service": "leadpulse360"}


@app.post(
    "/api/v1/leads",
    response_model=LeadTriageResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Triage"],
)
def triage_lead(lead: InboundLead) -> LeadTriageResponse:
    """Evaluate an inbound lead payload and return routing instructions."""
    try:
        score_res = calculate_lead_score(lead, DEFAULT_CONFIG)
        decision = determine_lead_route(lead, score_res, DEFAULT_CONFIG)
        logger.log_decision(lead, score_res, decision)

        return LeadTriageResponse(
            status="success",
            lead_name=f"{lead.first_name} {lead.last_name}",
            work_email=lead.work_email,
            score=score_res,
            routing=decision,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Triage pipeline failed: {str(exc)}",
        ) from exc


@app.get("/api/v1/analytics", tags=["Analytics"])
def get_analytics() -> Dict[str, Any]:
    """Return real-time triage distribution and score analytics."""
    records = logger.read_records()
    summary = AnalyticsSummary(records).compute_summary()
    return {"status": "success", "analytics": summary}

@app.post(
    "/api/v1/webhooks/form",
    response_model=LeadTriageResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Webhooks"],
)
async def ingest_form_webhook(payload: Dict[str, Any]) -> LeadTriageResponse:
    """Normalize raw inbound form webhooks and run through triage engine."""
    full_name = str(payload.get("full_name") or payload.get("name") or "").strip()
    first_name = str(payload.get("first_name") or "").strip()
    last_name = str(payload.get("last_name") or "").strip()

    if not first_name and full_name:
        parts = full_name.split()
        first_name = parts[0] if parts else "Anonymous"
        last_name = " ".join(parts[1:]) if len(parts) > 1 else "Unknown"

    work_email = str(payload.get("work_email") or payload.get("email") or "").strip()
    company_name = str(payload.get("company_name") or payload.get("company") or "Independent").strip()

    raw_size = payload.get("company_size", 10)
    try:
        company_size = int(float(str(raw_size).split("-")[0].replace("+", "").strip()))
    except (ValueError, TypeError):
        company_size = 10

    raw_budget = str(payload.get("annual_budget") or payload.get("budget") or "0")
    cleaned_budget = "".join(ch for ch in raw_budget if ch.isdigit() or ch == ".")
    annual_budget = float(cleaned_budget) if cleaned_budget else 0.0

    raw_urgency = payload.get("urgency_months", 3)
    try:
        urgency_months = int(float(str(raw_urgency).replace("+", "").strip()))
    except (ValueError, TypeError):
        urgency_months = 3

    industry = str(payload.get("industry") or "Technology").strip()
    notes = str(payload.get("message") or payload.get("notes") or payload.get("use_case_notes") or "").strip()
    src = str(payload.get("source") or "inbound_form_webhook").strip()

    normalized_lead = InboundLead(
        first_name=first_name or "Anonymous",
        last_name=last_name or "Unknown",
        work_email=work_email,
        company_name=company_name or "Independent",
        company_size=max(1, company_size),
        annual_budget=annual_budget,
        industry=industry or "Technology",
        urgency_months=max(1, urgency_months),
        use_case_notes=f"[{src}] {notes}".strip(),
    )

    return triage_lead(normalized_lead)
