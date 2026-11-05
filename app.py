import pandas as pd
import streamlit as st

from leadpulse.analytics import AnalyticsSummary
from leadpulse.audit import AuditLogger
from leadpulse.config import DEFAULT_CONFIG, ScoringConfig
from leadpulse.routing import determine_lead_route
from leadpulse.schemas import InboundLead
from leadpulse.scoring import calculate_lead_score

st.set_page_config(
    page_title="LeadPulse 360 | Enterprise Decision Engine",
    page_icon="⚡",
    layout="wide",
)

st.title("⚡ LeadPulse 360")
st.caption("Automated Enterprise Lead Decision, Scoring and Triage Engine")

with st.sidebar:
    st.header("⚙️ Scoring Calibration")
    vip_thresh = st.slider("VIP Score Threshold", 70, 95, DEFAULT_CONFIG.threshold_vip, 5)
    qual_thresh = st.slider("Qualified Threshold", 50, 75, DEFAULT_CONFIG.threshold_qualified, 5)
    nurture_thresh = st.slider("Nurture Threshold", 25, 45, DEFAULT_CONFIG.threshold_nurture, 5)

    active_config = ScoringConfig(
        threshold_vip=vip_thresh,
        threshold_qualified=qual_thresh,
        threshold_nurture=nurture_thresh,
    )

logger = AuditLogger()

tab_eval, tab_audit, tab_analytics = st.tabs(
    [
        "📥 Live Evaluation",
        "📜 Audit Trail",
        "📊 Pipeline Analytics",
    ]
)

with tab_eval:
    st.subheader("Process Inbound Lead")
    with st.form("lead_intake_form"):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name", value="Elena")
            last_name = st.text_input("Last Name", value="Rostova")
            work_email = st.text_input("Work Email", value="elena@finscale.io")
            company_name = st.text_input("Company Name", value="FinScale Inc")
        with col2:
            company_size = st.number_input(
                "Employee Headcount", min_value=1, max_value=500000, value=650, step=25
            )
            annual_budget = st.number_input(
                "Annual Budget (USD)",
                min_value=0.0,
                max_value=10000000.0,
                value=85000.0,
                step=5000.0,
            )
            urgency_months = st.selectbox(
                "Decision Timeline",
                options=[1, 3, 6, 12],
                format_func=lambda x: f"Within {x} month(s)",
            )
            industry = st.selectbox(
                "Industry",
                options=["Fintech", "SaaS", "Healthcare", "E-commerce", "Manufacturing", "Other"],
            )

        use_case_notes = st.text_area(
            "Use Case Scope",
            value="Enterprise migration and triage orchestration.",
        )
        submitted = st.form_submit_button("⚡ Evaluate and Route Lead", width="stretch")

    if submitted:
        try:
            lead = InboundLead(
                first_name=first_name,
                last_name=last_name,
                work_email=work_email,
                company_name=company_name,
                company_size=company_size,
                annual_budget=annual_budget,
                industry=industry,
                urgency_months=urgency_months,
                use_case_notes=use_case_notes,
            )
            score_res = calculate_lead_score(lead, active_config)
            decision = determine_lead_route(lead, score_res, active_config)
            logger.log_decision(lead, score_res, decision)

            st.success("Decision calculated and audit trail recorded successfully!")

            m1, m2, m3 = st.columns(3)
            m1.metric("Lead Score", f"{score_res.total_score} / 100")
            m2.metric("Route Destination", decision.destination.value)
            m3.metric("Response SLA", f"{decision.sla_hours} Hours")

            st.markdown("#### Score Breakdown")
            st.json(score_res.breakdown)

            st.markdown("#### Routing Verdict")
            action_info = (
                f"**Target Queue:** `{decision.target_queue}`\n\n"
                f"**Action:** {decision.action_required}\n\n"
                f"**Reason:** {decision.decision_reason}"
            )
            st.info(action_info)
        except Exception as e:
            st.error(f"Validation Error: {e}")

with tab_audit:
    st.subheader("Black-Box Decision Audit Records")
    current_records = logger.read_records()
    if not current_records:
        st.info("No decision records found yet. Submit a lead through Tab 1 to populate.")
    else:
        flat_records = [
            {
                "Timestamp (UTC)": r.timestamp_utc,
                "Name": f"{r.lead.first_name} {r.lead.last_name}",
                "Email": r.lead.work_email,
                "Company": r.lead.company_name,
                "Budget ($)": f"${r.lead.annual_budget:,.2f}",
                "Score": r.score_result.total_score,
                "Destination": r.routing_decision.destination.value,
                "Target Queue": r.routing_decision.target_queue,
            }
            for r in current_records
        ]
        st.dataframe(pd.DataFrame(flat_records), width="stretch")

with tab_analytics:
    st.subheader("Triage Pipeline Health")
    current_records = logger.read_records()
    analytics = AnalyticsSummary(current_records)
    summary = analytics.compute_summary()

    a1, a2, a3 = st.columns(3)
    a1.metric("Total Leads Processed", summary["total_leads"])
    a2.metric("Average Score", f"{summary['average_score']} / 100")
    total_val = summary["total_pipeline_budget"]
    a3.metric("Total Pipeline Value", f"${total_val:,.2f}")

    if summary["total_leads"] > 0:
        st.markdown("#### Routing Tier Breakdown")
        df_tiers = pd.DataFrame(
            list(summary["tier_counts"].items()),
            columns=["Routing Tier", "Count"],
        )
        st.bar_chart(df_tiers.set_index("Routing Tier"))
