# LeadPulse 360 | Enterprise Decision & Triage Engine

LeadPulse 360 is an automated lead intake, evaluation, and triage engine designed to replace manual sales triage with deterministic, auditable routing workflows.

---

## Core Capabilities

- **Strict Schema Validation**: Sanitizes names, checks emails, and enforces non-negative budgets using Pydantic v2.
- **Parametric Scoring Engine**: Weighted scoring matrix evaluating budget, headcount, buying urgency, and corporate email verification.
- **Deterministic SLA Routing**:
  - **VIP Tier** (Score >= 80): Immediate Slack alert to Enterprise AE (1h SLA).
  - **Qualified Tier** (Score >= 60): Round-robin SDR queue assignment (24h SLA).
  - **Nurture Tier** (Score >= 35): Automated educational email cadence (72h SLA).
  - **Disqualified**: Suppressed outreach, logged with deterministic audit reasons.
- **Append-Only Audit Trail**: Every decision is written to .jsonl for compliance and post-mortem review.
- **Real-Time Analytics UI**: Streamlit dashboard with calibration controls, audit inspection, and triage health metrics.

---

## Quickstart Guide

### 1. Execute Automated Test Suite
uv run pytest -v

### 2. Verify Code Quality & Style
uv run ruff check .

### 3. Launch Interactive Engine Dashboard
uv run streamlit run app.py