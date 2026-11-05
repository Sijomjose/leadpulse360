import pytest
from pydantic import ValidationError

from leadpulse.schemas import InboundLead


def test_valid_lead_creation():
    lead = InboundLead(
        first_name="  Sarah  ",
        last_name="Connor",
        work_email="s.connor@cyberdyne.com",
        company_name="Cyberdyne Systems",
        company_size=500,
        annual_budget=75000.0,
        industry="Robotics",
        urgency_months=2,
        use_case_notes="Automated inspection system",
    )
    assert lead.first_name == "Sarah"
    assert lead.is_corporate_domain is True
    assert lead.email_domain == "cyberdyne.com"


def test_invalid_email_format():
    with pytest.raises(ValidationError):
        InboundLead(
            first_name="John",
            last_name="Doe",
            work_email="not-an-email",
            company_name="Acme",
            company_size=10,
            annual_budget=5000.0,
            industry="Retail",
            urgency_months=3,
        )


def test_negative_budget_rejected():
    with pytest.raises(ValidationError):
        InboundLead(
            first_name="John",
            last_name="Doe",
            work_email="john@acme.com",
            company_name="Acme",
            company_size=10,
            annual_budget=-500.0,
            industry="Retail",
            urgency_months=3,
        )


def test_free_mailbox_detection():
    lead = InboundLead(
        first_name="Alice",
        last_name="Smith",
        work_email="alice.test@gmail.com",
        company_name="Freelance",
        company_size=1,
        annual_budget=1000.0,
        industry="Design",
        urgency_months=6,
    )
    assert lead.is_corporate_domain is False
    assert lead.email_domain == "gmail.com"
