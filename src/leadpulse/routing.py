from enum import Enum

from pydantic import BaseModel, Field

from leadpulse.config import DEFAULT_CONFIG, ScoringConfig
from leadpulse.schemas import InboundLead
from leadpulse.scoring import ScoreResult


class RouteDestination(str, Enum):
    VIP = "VIP"
    QUALIFIED = "QUALIFIED"
    NURTURE = "NURTURE"
    DISQUALIFIED = "DISQUALIFIED"


class RoutingDecision(BaseModel):
    destination: RouteDestination
    target_queue: str
    action_required: str
    decision_reason: str
    sla_hours: int = Field(..., ge=0)


def determine_lead_route(
    lead: InboundLead,
    score_result: ScoreResult,
    config: ScoringConfig = DEFAULT_CONFIG,
) -> RoutingDecision:
    score = score_result.total_score

    # Rule 1: VIP Tier (High score, enterprise/mid-market, immediate attention)
    if score >= config.threshold_vip:
        return RoutingDecision(
            destination=RouteDestination.VIP,
            target_queue="enterprise_ae_immediate",
            action_required="Send instant Slack alert to on-duty Senior AE for direct outreach.",
            decision_reason=(
                f"Score {score}/100 exceeds VIP threshold "
                f"({config.threshold_vip}). High-intent enterprise lead."
            ),
            sla_hours=1,
        )

    # Rule 2: Qualified Tier (Solid mid-market or growth prospect)
    if score >= config.threshold_qualified:
        return RoutingDecision(
            destination=RouteDestination.QUALIFIED,
            target_queue="sdr_outreach_queue",
            action_required="Assign to standard SDR round-robin queue for personalized follow-up.",
            decision_reason=(
                f"Score {score}/100 meets qualification threshold ({config.threshold_qualified})."
            ),
            sla_hours=24,
        )

    # Rule 3: Nurture Tier (Small business or long-term evaluation)
    if score >= config.threshold_nurture:
        return RoutingDecision(
            destination=RouteDestination.NURTURE,
            target_queue="automated_nurture_drip",
            action_required="Enroll lead into educational 6-week email drip campaign.",
            decision_reason=(
                f"Score {score}/100 indicates future potential; "
                "not ready for immediate human outreach."
            ),
            sla_hours=72,
        )

    # Rule 4: Disqualified (Low intent, negligible budget, or personal mailbox)
    reasons = []
    if not lead.is_corporate_domain:
        reasons.append("public/free email domain")
    if lead.annual_budget < config.budget_micro_min:
        reasons.append("budget below minimum entry threshold")
    if lead.urgency_months > 6:
        reasons.append("timeline beyond active buying window")

    reason_str = ", ".join(reasons) if reasons else "insufficient qualification signals"

    return RoutingDecision(
        destination=RouteDestination.DISQUALIFIED,
        target_queue="archive_disqualified",
        action_required="Log rejection reason and suppress active sales cadences.",
        decision_reason=(
            f"Score {score}/100 below minimum threshold "
            f"({config.threshold_nurture}). Key factors: {reason_str}."
        ),
        sla_hours=0,
    )
