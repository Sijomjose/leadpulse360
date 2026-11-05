"""Seed realistic multi-tier enterprise leads for client demonstrations."""

from leadpulse.audit import AuditLogger
from leadpulse.config import DEFAULT_CONFIG
from leadpulse.routing import determine_lead_route
from leadpulse.schemas import InboundLead
from leadpulse.scoring import calculate_lead_score

DEMO_LEADS = [
    InboundLead(
        first_name="Marcus",
        last_name="Vance",
        work_email="marcus@apexcloud.io",
        company_name="Apex Cloud Systems",
        company_size=1200,
        annual_budget=140000.0,
        industry="SaaS",
        urgency_months=1,
        use_case_notes="Global migration across 4 regions. Needs SOC2 enterprise SLA.",
    ),
    InboundLead(
        first_name="Sarah",
        last_name="Chen",
        work_email="schen@healthmatrix.org",
        company_name="HealthMatrix Labs",
        company_size=350,
        annual_budget=45000.0,
        industry="Healthcare",
        urgency_months=3,
        use_case_notes="HIPAA compliance data processing pilot for oncology division.",
    ),
    InboundLead(
        first_name="David",
        last_name="Miller",
        work_email="dmiller@retailstream.com",
        company_name="RetailStream Ltd",
        company_size=80,
        annual_budget=15000.0,
        industry="E-commerce",
        urgency_months=6,
        use_case_notes="Evaluating modern CRM and triage tools for Q3 budget planning.",
    ),
    InboundLead(
        first_name="Tom",
        last_name="Tester",
        work_email="tommy99@yahoo.com",
        company_name="Self-Employed",
        company_size=1,
        annual_budget=500.0,
        industry="Other",
        urgency_months=12,
        use_case_notes="Curious about features.",
    ),
]


def run_seed():
    logger = AuditLogger()
    print(">>> Seeding LeadPulse 360 demo dataset...")
    for lead in DEMO_LEADS:
        score_res = calculate_lead_score(lead, DEFAULT_CONFIG)
        decision = determine_lead_route(lead, score_res, DEFAULT_CONFIG)
        logger.log_decision(lead, score_res, decision)
        name = f"{lead.first_name} {lead.last_name}"
        print(
            f"  [+] Logged: {name:<18} | Score: {score_res.total_score:>3}/100 | Tier: {decision.destination.value}"
        )
    print(">>> Demo dataset seeded successfully!")


if __name__ == "__main__":
    run_seed()