from pydantic import BaseModel


class ScoringConfig(BaseModel):
    # Budget weights (max 35 pts)
    budget_enterprise_min: float = 100_000.0  # +35 pts
    budget_midmarket_min: float = 30_000.0  # +25 pts
    budget_smb_min: float = 10_000.0  # +15 pts
    budget_micro_min: float = 1_000.0  # +5 pts

    # Company size weights (max 25 pts)
    size_enterprise_min: int = 1_000  # +25 pts
    size_midmarket_min: int = 250  # +20 pts
    size_growth_min: int = 50  # +15 pts
    size_small_min: int = 10  # +10 pts

    # Urgency weights (max 20 pts)
    urgency_immediate_max_months: int = 1  # +20 pts
    urgency_near_term_max_months: int = 3  # +15 pts
    urgency_medium_term_max_months: int = 6  # +10 pts

    # Domain bonus & penalties (max 20 pts)
    corporate_domain_bonus: int = 20  # +20 pts
    free_domain_penalty: int = -10  # -10 pts

    # Triage Routing Thresholds
    threshold_vip: int = 80  # >= 80 -> VIP
    threshold_qualified: int = 60  # >= 60 -> Qualified
    threshold_nurture: int = 35  # >= 35 -> Nurture
    # < 35 -> Disqualified


DEFAULT_CONFIG = ScoringConfig()
