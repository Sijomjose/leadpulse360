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
