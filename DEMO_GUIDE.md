# LeadPulse 360 | Enterprise Client Demo Playbook

Use this 3-minute structured walk-through when pitching revenue operations heads, sales VPs, and technical founders.

---

## The Pitch (First 45 Seconds)

> "Most B2B lead ingestion pipelines leak pipeline revenue in two ways: slow SLA response times for high-value enterprise accounts, and sales teams wasting hours manually reading junk submissions. LeadPulse 360 solves this with a deterministic, auditable decision engine built on Python 3.12 and Pydantic v2. It validates, scores, and routes inbound leads in under 5 milliseconds—with a permanent append-only audit trail."

---

## Live Walkthrough Sequence (2 Minutes)

### 1. The High-Value Enterprise Flow
- **Input**: Enterprise tier ($85k budget, 650 headcount, corporate domain).
- **Showcase**:
  - Score: **85 / 100**
  - Destination: **VIP**
  - SLA: **1 Hour**
  - Queue: `enterprise_ae_immediate`
- **Key Takeaway**: High-value opportunities bypass manual queues and trigger instantaneous senior AE outreach.

### 2. The Negative Qualification & Anti-Spam Branch
- **Input**: Freemail domain (`bob123@gmail.com`), $250 budget, 1 headcount.
- **Showcase**:
  - Score: **0 / 100**
  - Destination: **DISQUALIFIED**
  - SLA: **0 Hours**
  - Queue: `archive_disqualified`
- **Key Takeaway**: Zero rep time wasted on non-ICP traffic, while logging precise disqualification reasons for marketing attribution.

### 3. Dynamic Threshold Calibration (Sidebar)
- Adjust the **VIP Threshold** slider from `80` to `90`.
- Show how the decision policy updates dynamically without code modification or service restarts.

### 4. Enterprise Auditability & Pipeline Health
- **Audit Trail Tab**: Show the immutable `.jsonl` black-box records with exact timestamps, contact metadata, and rationale strings.
- **Pipeline Analytics Tab**: Show real-time portfolio triage distributions, average score health, and aggregate pipeline volume.

---

## Handling Client Technical Questions

| Question | Answer |
|---|---|
| *"Can this integrate into HubSpot or Salesforce?"* | Yes. The schema models and routing engine run cleanly inside AWS Lambda, FastAPI webhooks, or Google Cloud Run to sync directly with CRM REST APIs. |
| *"Why not just use an LLM for routing?"* | LLMs are non-deterministic, cost 100x more per inference, and introduce latency (1–3s vs <5ms). LeadPulse uses deterministic schema contracts, with LLMs reserved for optional unstructured note extraction. |
| *"Is the audit trail compliant?"* | Yes. The engine logs structured JSONL records capturing every input parameter and decision state, ideal for SOC2, ISO 27001, and RevOps governance. |