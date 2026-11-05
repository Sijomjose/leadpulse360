# ⚡ LeadPulse 360

**Enterprise Inbound Lead Triage, Scoring, and Routing Engine**

LeadPulse 360 is a production-grade backend engine designed to automate the intake, qualification, and routing of enterprise leads. Built with **Python 3.12**, **Pydantic v2**, and **FastAPI**, it delivers deterministic decision policies with sub-5ms latency and an immutable black-box audit trail.

---

## 🎯 Architecture & Capabilities

- **Pydantic v2 Strict Contracts:** Sanitizes inputs, validates corporate emails, and rejects invalid structures before execution.
- **Deterministic Multi-Factor Scoring:** Weighted arithmetic scoring (0–100) assessing budget, employee headcount, urgency, and domain authority.
- **SLA-Driven Routing Engine:** Dispatches leads to dedicated queues (`VIP`, `Qualified`, `Nurture`, `Disqualified`) with strict response SLAs.
- **Black-Box Audit Logging:** Append-only structured JSONL records capturing input payloads, scoring breakdowns, and routing justifications for SOC2/ISO compliance.
- **Dual Interfaces:**
  - **REST Webhook API (FastAPI):** Automated endpoint for CRM, Typeform, or Webflow form integrations.
  - **Live Executive Dashboard (Streamlit):** Visual triage station with dynamic threshold calibration and pipeline analytics.

---

## 🚀 Quickstart

### 1. Environment Setup
Install dependencies with [uv](https://docs.astral.sh/uv/):
```powershell
uv sync