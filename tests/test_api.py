"""Automated endpoint tests for FastAPI lead triage router."""

from fastapi.testclient import TestClient

from leadpulse.api import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "leadpulse360"}


def test_triage_enterprise_lead_endpoint():
    payload = {
        "first_name": "Rachel",
        "last_name": "Green",
        "work_email": "rachel@enterprisehub.io",
        "company_name": "EnterpriseHub",
        "company_size": 800,
        "annual_budget": 120000.0,
        "industry": "Fintech",
        "urgency_months": 1,
        "use_case_notes": "Cloud migration compliance orchestration.",
    }
    response = client.post("/api/v1/leads", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["routing"]["destination"] == "VIP"
    assert data["routing"]["sla_hours"] == 1


def test_triage_invalid_email_rejection():
    payload = {
        "first_name": "Bad",
        "last_name": "Lead",
        "work_email": "invalid-email-string",
        "company_name": "FailCorp",
        "company_size": 10,
        "annual_budget": 5000.0,
        "industry": "Other",
        "urgency_months": 12,
        "use_case_notes": "Testing invalid payload rejection.",
    }
    response = client.post("/api/v1/leads", json=payload)
    assert response.status_code == 422
