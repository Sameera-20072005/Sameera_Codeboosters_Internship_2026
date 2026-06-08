"""
Agentic Data Engineering Pipeline — app.py
Streamlit entry point orchestrating all 6 agents.
"""
from __future__ import annotations

import os
import sys

# ── sys.path guard ─────────────────────────────────────────────────────────────
_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import streamlit as st
from typing import NamedTuple
from dotenv import load_dotenv

from services.llm_service        import GroqService
from services.storage_service    import StorageService
from agents.dataset_agent        import DatasetAgent
from agents.cleaning_agent       import CleaningAgent
from agents.transformation_agent import TransformationAgent
from agents.spark_agent          import SparkAgent
from agents.analytics_agent      import AnalyticsAgent
from agents.report_agent         import ReportAgent
from utils.logger                import get_logger

load_dotenv()
logger = get_logger(__name__)

st.set_page_config(
    page_title="Agentic Data Pipeline",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Domain presets ─────────────────────────────────────────────────────────────
DOMAIN_PROMPTS: dict[str, str] = {
    "Telecom": (
        "Generate a telecom customer churn dataset. Include: customer_id, age, gender, "
        "tenure_months, monthly_charges, total_charges, contract_type, payment_method, "
        "internet_service, tech_support, churn (Yes/No)."
    ),
    "Banking": (
        "Generate a bank customer loan default dataset. Include: customer_id, age, income, "
        "loan_amount, loan_term, credit_score, employment_type, default (0/1), "
        "debt_to_income_ratio, num_credit_lines."
    ),
    "Retail": (
        "Generate a retail sales dataset. Include: transaction_id, customer_id, "
        "product_category, product_name, quantity, unit_price, total_amount, "
        "store_region, payment_method, date."
    ),
    "Healthcare": (
        "Generate a patient readmission dataset. Include: patient_id, age, gender, "
        "diagnosis, length_of_stay, num_procedures, insurance_type, "
        "readmitted (Yes/No), num_medications, discharge_disposition."
    ),
    "Custom": "",
}


# ── Services container ─────────────────────────────────────────────────────────
class PipelineServices(NamedTuple):
    llm:             GroqService
    storage:         StorageService
    dataset_agent:   DatasetAgent
    cleaning_agent:  CleaningAgent
    transform_agent: TransformationAgent
    spark_agent:     SparkAgent
    analytics_agent: AnalyticsAgent
    report_agent:    ReportAgent


@st.cache_resource(show_spinner=False)
def _init_services() -> PipelineServices | None:
    """Initialise and cache all pipeline services. Returns None on config error."""
    try:
        llm     = GroqService()
        storage = StorageService()
        return PipelineServices(
            llm=llm,
            storage=storage,
            dataset_agent=DatasetAgent(llm, storage),
            cleaning_agent=CleaningAgent(storage),
            transform_agent=TransformationAgent(storage),
            spark_agent=SparkAgent(storage),
            analytics_agent=AnalyticsAgent(llm, storage),
            report_agent=ReportAgent(storage),
        )
    except EnvironmentError as exc:
        logger.critical("Service init failed: %s", exc)
        return None


# ── Pipeline runner ────────────────────────────────────────────────────────────
def run_pipeline(
    svc: PipelineServices,
    description: str,
    domain: str,
    record_count: int,
    progress_bar,
    status_text,
) -> dict:
    """Execute all 6 agents sequentially, updating Streamlit progress."""
    results: dict = {}

    def _step(msg: str, pct: float) -> None:
        status_text.markdown(f"**{msg}**")
        progress_bar.progress(pct)
        logger.info("Pipeline | %s", msg)

    # 1 — Dataset Generation
    _step("🤖 DatasetAgent: Generating synthetic dataset...", 0.10)
    df_raw   = svc.dataset_agent.generate_dataset(description, record_count, domain)
    raw_path = svc.dataset_agent.save_dataset(df_raw, domain.lower())
    results["df_raw"]   = df_raw
    results["raw_path"] = raw_path

    # 2 — Cleaning
    _step("🧹 CleaningAgent: Removing duplicates & imputing missing values...", 0.25)
    df_clean, c_report  = svc.cleaning_agent.clean_data(df_raw)
    svc.cleaning_agent.save_cleaned(df_clean, domain.lower())
    cleaning_report     = svc.cleaning_agent.generate_cleaning_report(c_report)
    results["df_clean"]        = df_clean
    results["cleaning_report"] = cleaning_report

    # 3 — Transformation
    _step("⚙️ TransformationAgent: Feature engineering, encoding & scaling...", 0.42)
    df_eng, new_feats = svc.transform_agent.engineer_features(df_clean)
    df_enc, enc_maps  = svc.transform_agent.encode_features(df_eng)
    df_scaled, _      = svc.transform_agent.scale_features(df_enc)
    svc.transform_agent.save_transformed(df_scaled, domain.lower())
    results["df_transformed"] = df_scaled
    results["new_features"]   = new_feats
    results["encoding_maps"]  = enc_maps

    # 4 — Spark / Pandas analytics
    _step("⚡ SparkAgent: Running distributed aggregations...", 0.58)
    svc.spark_agent.initialize_spark()
    spark_obj  = svc.spark_agent.process_dataset(df_scaled)
    spark_dict = svc.spark_agent.generate_spark_metrics(spark_obj)
    svc.spark_agent.save_metrics(spark_obj)
    svc.spark_agent.stop()
    results["spark_metrics"] = spark_dict

    # 5 — KPIs & Insights
    _step("📊 AnalyticsAgent: Computing KPIs and generating insights...", 0.72)
    kpis     = svc.analytics_agent.calculate_kpis(df_clean, cleaning_report)
    insights = svc.analytics_agent.generate_insights(kpis, description)
    results["kpis"]     = kpis
    results["insights"] = insights

    # 6 — Reports
    _step("📝 ReportAgent: Generating Markdown and PDF reports...", 0.88)
    md_path  = svc.report_agent.generate_markdown(
        description, df_raw, df_clean, kpis, spark_dict, insights, cleaning_report
    )
    pdf_path = svc.report_agent.generate_pdf(description, kpis, spark_dict, insights)
    results["md_path"]  = md_path
    results["pdf_path"] = pdf_path

    _step("✅ Pipeline complete!", 1.0)
    return results


# ── Main ───────────────────────────────────────────────────────────────────────
def main() -> None:

    # Service init
    svc = _init_services()
    if svc is None:
        st.error(
            "⚠️ **GROQ_API_KEY is missing.**\n\n"
            "Add it to your `.env` file and restart:\n```\nGROQ_API_KEY=your_key_here\n```"
        )
        st.stop()

    # Session state defaults
    for key, default in [("results", None), ("running", False)]:
        if key not in st.session_state:
            st.session_state[key] = default

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.title("⚙️ Pipeline Config")
        st.markdown("---")
        domain = st.selectbox(
            "📂 Dataset Domain",
            options=list(DOMAIN_PROMPTS.keys()),
            index=0,
        )
        record_count = st.slider(
            "📊 Record Count",
            min_value=50, max_value=500, value=150, step=50,
        )
        st.markdown("---")
        st.markdown("**6 Pipeline Agents:**")
        for a in ["1. DatasetAgent", "2. CleaningAgent", "3. TransformationAgent",
                  "4. SparkAgent", "5. AnalyticsAgent", "6. ReportAgent"]:
            st.markdown(f"- {a}")
        st.markdown("---")
        st.caption("Groq · PySpark · Scikit-Learn · ReportLab")

    # ── Header ────────────────────────────────────────────────────────────────
    st.title("⚙️ Agentic Data Engineering Pipeline")
    st.markdown(
        "Describe your dataset in plain English. "
        "The pipeline will **generate → clean → transform → analyse → report** it automatically."
    )
    st.markdown("---")

    col_in, col_out = st.columns([1, 1], gap="large")

    # ── Input panel ───────────────────────────────────────────────────────────
    with col_in:
        st.subheader("📝 Dataset Request")
        preset      = DOMAIN_PROMPTS.get(domain, "")
        description = st.text_area(
            "Describe your dataset",
            value=preset,
            placeholder="e.g. Generate a telecom customer churn dataset with 200 records...",
            height=200,
            max_chars=800,
        )
        st.caption(f"{len(description)} / 800 characters")

        run_clicked = st.button(
            "🚀 Run Pipeline",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.running,
        )

    # ── Execution ─────────────────────────────────────────────────────────────
    if run_clicked:
        if not description.strip():
            st.warning("⚠️ Please enter a dataset description.")
        else:
            st.session_state.running = True
            st.session_state.results = None
            progress_bar = st.progress(0.0)
            status_text  = st.empty()
            try:
                results = run_pipeline(
                    svc, description, domain, record_count,
                    progress_bar, status_text,
                )
                st.session_state.results = results
            except Exception as exc:
                st.error(f"❌ Pipeline failed: {exc}")
                logger.error("Pipeline error: %s", exc, exc_info=True)
            finally:
                st.session_state.running = False
                st.rerun()

    # ── Output panel ──────────────────────────────────────────────────────────
    with col_out:
        st.subheader("📊 Pipeline Output")
        res = st.session_state.results

        if res is None:
            st.info("Pipeline results will appear here after execution.")
        else:
            st.success("✅ Pipeline completed successfully!")

            # Dataset preview
            with st.expander("📄 Raw Dataset Preview", expanded=True):
                df_raw = res.get("df_raw")
                if df_raw is not None:
                    st.dataframe(df_raw.head(10), use_container_width=True)
                    st.caption(f"Shape: {df_raw.shape[0]:,} rows × {df_raw.shape[1]} cols")

            # Cleaning summary
            with st.expander("🧹 Cleaning Summary"):
                cr = res.get("cleaning_report", {})
                m1, m2, m3 = st.columns(3)
                m1.metric("Original Rows",     cr.get("original_rows", 0))
                m2.metric("Duplicates Removed", cr.get("duplicates_removed", 0))
                m3.metric("Final Rows",         cr.get("final_rows", 0))
                renamed = cr.get("columns_renamed", [])
                if renamed:
                    st.markdown("**Renamed:** " + " | ".join(renamed[:5]))

            # KPI dashboard
            with st.expander("📊 KPI Dashboard", expanded=True):
                kpis = res.get("kpis", {})
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("Records",        kpis.get("total_records", 0))
                k2.metric("Columns",        kpis.get("total_columns", 0))
                k3.metric("Missing Values", kpis.get("missing_values", 0))
                k4.metric("Memory (KB)",    kpis.get("memory_usage_kb", 0))
                if "churn_rate" in kpis:
                    st.metric("Churn Rate", f"{float(kpis['churn_rate']):.2%}")
                if "total_revenue" in kpis:
                    st.metric("Total Revenue", f"{float(kpis['total_revenue']):,.2f}")

            # Spark / Pandas metrics
            sm = res.get("spark_metrics", {})
            engine_label = sm.get("engine", "pandas").upper()
            with st.expander(f"⚡ {engine_label} Metrics"):
                s1, s2 = st.columns(2)
                s1.metric("Rows Processed", f"{sm.get('row_count', 0):,}")
                s2.metric("Columns",        sm.get("col_count", 0))
                num_sum = sm.get("numeric_summary", {})
                if num_sum:
                    import pandas as pd
                    st.dataframe(pd.DataFrame(num_sum).T, use_container_width=True)

            # AI Insights
            with st.expander("🤖 AI Business Insights", expanded=True):
                st.markdown(res.get("insights", "_No insights generated._"))

            # Feature engineering summary
            with st.expander("🔧 Transformation Summary"):
                new_feats = res.get("new_features", [])
                st.markdown(f"**New Features Added:** {len(new_feats)}")
                if new_feats:
                    st.markdown(", ".join(f"`{f}`" for f in new_feats))
                enc_maps = res.get("encoding_maps", {})
                st.markdown(f"**Columns Encoded:** {len(enc_maps)}")

            # Download buttons
            st.markdown("#### 💾 Download Reports")
            d1, d2 = st.columns(2)

            md_path = res.get("md_path", "")
            if md_path:
                try:
                    md_text = StorageService.load_text(md_path)
                    d1.download_button(
                        "📄 Download Markdown",
                        data=md_text,
                        file_name="pipeline_report.md",
                        mime="text/markdown",
                        use_container_width=True,
                    )
                except Exception:
                    pass

            pdf_path = res.get("pdf_path", "")
            if pdf_path:
                try:
                    abs_pdf = os.path.join(_ROOT, pdf_path)
                    with open(abs_pdf, "rb") as f:
                        d2.download_button(
                            "📋 Download PDF",
                            data=f.read(),
                            file_name="pipeline_report.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )
                except Exception:
                    d2.caption("PDF unavailable — install `reportlab`.")

    # ── History expander ──────────────────────────────────────────────────────
    if res := st.session_state.results:
        st.markdown("---")
        with st.expander("📁 Saved Artefact Paths"):
            st.markdown(f"- **Raw data:** `{res.get('raw_path', '—')}`")
            st.markdown(f"- **Report (MD):** `{res.get('md_path', '—')}`")
            pdf = res.get("pdf_path", "")
            st.markdown(f"- **Report (PDF):** `{pdf if pdf else 'not generated'}`")


if __name__ == "__main__":
    main()
