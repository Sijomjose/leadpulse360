from typing import Dict

from pydantic import BaseModel, Field

from leadpulse.config import DEFAULT_CONFIG, ScoringConfig
from leadpulse.schemas import InboundLead


class ScoreResult(BaseModel):
    total_score: int = Field(..., ge=0, le=100)
    breakdown: Dict[str, int]
    scoring_notes: list[str] = Field(default_factory=list)


def calculate_lead_score(lead: InboundLead, config: ScoringConfig = DEFAULT_CONFIG) -> ScoreResult:
    breakdown: Dict[str, int] = {}
    notes: list[str] = []

    # 1. Budget scoring (max 35 pts)
    if lead.annual_budget >= config.budget_enterprise_min:
        budget_pts = 35
        notes.append("Enterprise budget tier (>= )")
    elif lead.annual_budget >= config.budget_midmarket_min:
        budget_pts = 25
        notes.append("Mid-market budget tier (>= )")
    elif lead.annual_budget >= config.budget_smb_min:
        budget_pts = 15
        notes.append("SMB budget tier (>= )")
    elif lead.annual_budget >= config.budget_micro_min:
        budget_pts = 5
        notes.append("Micro budget tier")
    else:
        budget_pts = 0
        notes.append("Negligible or zero declared budget")
    breakdown["budget"] = budget_pts

    # 2. Company size scoring (max 25 pts)
    if lead.company_size >= config.size_enterprise_min:
        size_pts = 25
        notes.append(f"Enterprise headcount (>= {config.size_enterprise_min:,})")
    elif lead.company_size >= config.size_midmarket_min:
        size_pts = 20
        notes.append(f"Upper mid-market headcount (>= {config.size_midmarket_min})")
    elif lead.company_size >= config.size_growth_min:
        size_pts = 15
        notes.append(f"Growth headcount (>= {config.size_growth_min})")
    elif lead.company_size >= config.size_small_min:
        size_pts = 10
        notes.append("Small business headcount")
    else:
        size_pts = 5
        notes.append("Micro business or solopreneur headcount")
    breakdown["company_size"] = size_pts

    # 3. Urgency scoring (max 20 pts)
    if lead.urgency_months <= config.urgency_immediate_max_months:
        urgency_pts = 20
        notes.append("Immediate buying urgency (<= 1 month)")
    elif lead.urgency_months <= config.urgency_near_term_max_months:
        urgency_pts = 15
        notes.append("Near-term buying urgency (<= 3 months)")
    elif lead.urgency_months <= config.urgency_medium_term_max_months:
        urgency_pts = 10
        notes.append("Medium-term buying urgency (<= 6 months)")
    else:
        urgency_pts = 0
        notes.append("Low immediate urgency (> 6 months)")
    breakdown["urgency"] = urgency_pts

    # 4. Domain scoring (max 20 pts / penalty)
    if lead.is_corporate_domain:
        domain_pts = config.corporate_domain_bonus
        notes.append(f"Verified business domain ({lead.email_domain})")
    else:
        domain_pts = config.free_domain_penalty
        notes.append(f"Free public mailbox domain ({lead.email_domain})")
    breakdown["email_domain"] = domain_pts

    # Sum and clamp score to range [0, 100]
    raw_total = sum(breakdown.values())
    total_score = max(0, min(100, raw_total))

    return ScoreResult(total_score=total_score, breakdown=breakdown, scoring_notes=notes)
