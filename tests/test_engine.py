from leadpulse.routing import RouteDestination, determine_lead_route
from leadpulse.schemas import InboundLead
from leadpulse.scoring import calculate_lead_score


def test_enterprise_lead_routes_to_vip():
    lead = InboundLead(
        first_name="Victoria",
        last_name="Sterling",
        work_email="victoria@globalenterprises.com",
        company_name="Global Enterprises",
        company_size=2000,
        annual_budget=150000.0,
        industry="Financial Services",
        urgency_months=1,
    )
    score = calculate_lead_score(lead)
    decision = determine_lead_route(lead, score)

    # 35 (budget) + 25 (size) + 20 (urgency) + 20 (domain) = 100
    assert score.total_score == 100
    assert decision.destination == RouteDestination.VIP
    assert decision.sla_hours == 1


def test_disqualified_lead_free_email_low_budget():
    lead = InboundLead(
        first_name="Bob",
        last_name="Builder",
        work_email="bob123@gmail.com",
        company_name="Bob Handyman",
        company_size=1,
        annual_budget=200.0,
        industry="Services",
        urgency_months=12,
    )
    score = calculate_lead_score(lead)
    decision = determine_lead_route(lead, score)

    # 0 (budget) + 5 (size) + 0 (urgency) - 10 (domain penalty) clamped to 0
    assert score.total_score == 0
    assert decision.destination == RouteDestination.DISQUALIFIED
    assert "public/free email domain" in decision.decision_reason
