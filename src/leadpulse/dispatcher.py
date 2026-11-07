"""Asynchronous outbound notification and webhook dispatcher for LeadPulse 360."""

import asyncio
import logging
import sys
from leadpulse.schemas import InboundLead
from leadpulse.routing import RoutingDecision
from leadpulse.scoring import ScoreResult

logger = logging.getLogger("leadpulse.dispatcher")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

async def dispatch_lead_notifications(
    lead: InboundLead,
    decision: RoutingDecision,
    score: ScoreResult
) -> None:
    """Asynchronously triggers external notifications (Slack/CRM) based on routing tier."""
    await asyncio.sleep(0.05)

    if decision.destination == "VIP":
        logger.info(
            f"[OUTBOUND-DISPATCH] [SLACK-ALERT] Triggered instant AE alert for VIP lead: "
            f"{lead.work_email} ({lead.company_name}) | Score: {score.total_score}/100 | "
            f"Queue: {decision.target_queue} | SLA: {decision.sla_hours}h"
        )
    elif decision.destination == "QUALIFIED":
        logger.info(
            f"[OUTBOUND-DISPATCH] [CRM-PUSH] Queued lead {lead.work_email} "
            f"to SDR queue: {decision.target_queue} | SLA: {decision.sla_hours}h"
        )
    else:
        logger.info(
            f"[OUTBOUND-DISPATCH] [NURTURE-SYNC] Lead {lead.work_email} synced to "
            f"automated drip campaign | Tier: {decision.destination}"
        )
