from typing import Any, Dict, List

from leadpulse.audit import LeadAuditRecord


class AnalyticsSummary:
    def __init__(self, records: List[LeadAuditRecord]):
        self.records = records

    def compute_summary(self) -> Dict[str, Any]:
        total_leads = len(self.records)
        if total_leads == 0:
            return {
                "total_leads": 0,
                "tier_counts": {},
                "tier_percentages": {},
                "average_score": 0.0,
                "total_pipeline_budget": 0.0,
            }

        tier_counts: Dict[str, int] = {
            "VIP": 0,
            "QUALIFIED": 0,
            "NURTURE": 0,
            "DISQUALIFIED": 0,
        }
        total_score = 0
        total_budget = 0.0

        for r in self.records:
            dest = r.routing_decision.destination.value
            tier_counts[dest] = tier_counts.get(dest, 0) + 1
            total_score += r.score_result.total_score
            total_budget += r.lead.annual_budget

        avg_score = round(total_score / total_leads, 2)
        tier_pcts = {
            tier: round((count / total_leads) * 100, 1) for tier, count in tier_counts.items()
        }

        return {
            "total_leads": total_leads,
            "tier_counts": tier_counts,
            "tier_percentages": tier_pcts,
            "average_score": avg_score,
            "total_pipeline_budget": round(total_budget, 2),
        }
