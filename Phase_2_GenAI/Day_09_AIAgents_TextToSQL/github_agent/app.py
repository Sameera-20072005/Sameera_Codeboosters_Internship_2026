"""
Natural Language to GitHub Workflow Automation — app.py
Streamlit entry point.
"""

from __future__ import annotations

import sys
import os

# ── sys.path guard ────────────────────────────────────────────────────────────
_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import streamlit as st
from typing import NamedTuple
from dotenv import load_dotenv

from services.llm_service     import GroqLLMService
from services.github_service  import GitHubService
from services.history_service import HistoryService
from agent.workflow_agent     import WorkflowAgent
from utils.logger             import get_logger

load_dotenv()
logger = get_logger(__name__)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GitHub Workflow Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Services container ────────────────────────────────────────────────────────
class AppServices(NamedTuple):
    agent:   WorkflowAgent
    history: HistoryService


@st.cache_resource(show_spinner=False)
def _init_services() -> AppServices | None:
    """Initialise and cache all services. Returns None on config error."""
    try:
        llm     = GroqLLMService()
        github  = GitHubService()
        history = HistoryService()
        agent   = WorkflowAgent(
            llm_service=llm,
            github_service=github,
            history_service=history,
        )
        return AppServices(agent=agent, history=history)
    except EnvironmentError as exc:
        logger.critical("Service init failed: %s", exc)
        return None


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:

    # ── Service init ──────────────────────────────────────────────────────────
    svc = _init_services()
    if svc is None:
        st.error(
            "⚠️ **Configuration error.**\n\n"
            "Ensure both `GROQ_API_KEY` and `GITHUB_TOKEN` are set in your `.env` file, then restart."
        )
        st.stop()

    # ── Session state defaults ────────────────────────────────────────────────
    for key, default in [
        ("result", None),
        ("log_messages", []),
        ("running", False),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.title("🤖 GitHub Agent")
        st.markdown("---")

        visibility = st.radio(
            "🔒 Repository Visibility",
            options=["Public", "Private"],
            index=0,
        ).lower()

        st.markdown("---")

        st.markdown("**How it works:**")
        st.markdown(
            "1. Describe your project\n"
            "2. Agent parses requirements\n"
            "3. Plans execution steps\n"
            "4. Generates all files\n"
            "5. Creates GitHub repo\n"
            "6. Pushes everything\n"
            "7. Returns repo URL"
        )
        st.markdown("---")
        st.caption("Powered by Groq · LangChain · PyGithub")

    # ── Header ────────────────────────────────────────────────────────────────
    st.title("🤖 Natural Language → GitHub Repository")
    st.markdown(
        "Describe your project in plain English. "
        "The agent will scaffold a complete repository and push it to GitHub."
    )
    st.markdown("---")

    col_left, col_right = st.columns([1, 1], gap="large")

    # ── Input panel ───────────────────────────────────────────────────────────
    with col_left:
        st.subheader("📝 Project Description")
        user_request = st.text_area(
            "Describe your project",
            placeholder=(
                "e.g. Create a Python Flask Todo REST API with SQLite, "
                "GitHub Actions CI/CD, pytest tests, and Docker support."
            ),
            height=180,
            max_chars=1000,
        )
        st.caption(f"{len(user_request)} / 1000 characters")

        run_clicked = st.button(
            "🚀 Generate Repository",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.running,
        )

        # ── Example prompts ───────────────────────────────────────────────────
        st.markdown("**Example prompts:**")
        examples = [
            "Python FastAPI microservice with PostgreSQL, Docker, and pytest",
            "Node.js Express REST API with MongoDB and GitHub Actions CI",
            "Java Spring Boot application with Maven and unit tests",
        ]
        for ex in examples:
            if st.button(f"💡 {ex[:60]}", key=ex, use_container_width=True):
                st.session_state["prefill"] = ex
                st.rerun()

        # Apply prefill if set
        if "prefill" in st.session_state:
            user_request = st.session_state.pop("prefill")

    # ── Agent execution ───────────────────────────────────────────────────────
    error_slot = st.empty()

    if run_clicked:
        if not user_request.strip():
            error_slot.warning("⚠️ Please enter a project description.")
        else:
            st.session_state.running      = True
            st.session_state.result       = None
            st.session_state.log_messages = []

            log_messages: list[str] = []

            def _on_progress(msg: str) -> None:
                log_messages.append(msg)

            with st.spinner("🤖 Agent is working..."):
                result = svc.agent.run(
                    user_request=user_request,
                    visibility=visibility,
                    progress_callback=_on_progress,
                )

            st.session_state.result       = result
            st.session_state.log_messages = log_messages
            st.session_state.running      = False
            st.rerun()

    # ── Output panel ──────────────────────────────────────────────────────────
    with col_right:
        st.subheader("📊 Agent Output")
        result = st.session_state.result

        if result is None:
            st.info("Repository details will appear here after generation.")
        elif not result.success:
            st.error(f"❌ Agent failed: {result.error}")
            logger.error("Agent reported failure: %s", result.error)
        else:
            # ── Success banner ────────────────────────────────────────────────
            st.success("✅ Repository created successfully!")
            st.markdown(f"### 🔗 [{result.repository_name}]({result.repository_url})")
            st.code(result.repository_url)

            # ── Extracted intent ──────────────────────────────────────────────
            with st.expander("🔍 Extracted Intent", expanded=True):
                intent = result.intent
                c1, c2 = st.columns(2)
                c1.metric("Project Name", intent.get("project_name", "—"))
                c2.metric("Language",     intent.get("language", "—"))
                c1.metric("Framework",    intent.get("framework", "—") or "None")
                c2.metric("Database",     intent.get("database",  "—") or "None")
                flags = {
                    "Testing":    intent.get("testing_required", False),
                    "Docker":     intent.get("docker_required",  False),
                    "CI/CD":      intent.get("ci_required",      False),
                    "Visibility": intent.get("visibility", "public").title(),
                }
                for label, val in flags.items():
                    icon = "✅" if val is True else ("❌" if val is False else "ℹ️")
                    st.markdown(f"{icon} **{label}:** {val}")

            # ── Execution plan ────────────────────────────────────────────────
            with st.expander("📋 Execution Plan"):
                for i, step in enumerate(result.plan, 1):
                    st.markdown(f"{i}. `{step}`")

            # ── Generated files ───────────────────────────────────────────────
            with st.expander(f"📁 Generated Files ({len(result.files_generated)})"):
                for f in sorted(result.files_generated):
                    st.markdown(f"- `{f}`")

    # ── Agent log ─────────────────────────────────────────────────────────────
    if st.session_state.log_messages:
        st.markdown("---")
        with st.expander("🪵 Agent Log", expanded=False):
            for msg in st.session_state.log_messages:
                st.markdown(f"- {msg}")

    # ── History ───────────────────────────────────────────────────────────────
    st.markdown("---")
    with st.expander("🕑 Generation History", expanded=False):
        history = svc.history.load_history()
        if not history:
            st.info("No history yet.")
        else:
            if st.button("🗑️ Clear History", type="secondary", key="clear_history_btn"):
                svc.history.clear_history()
                st.success("History cleared.")
                st.rerun()

            for i, record in enumerate(history[:10]):
                c1, c2, c3 = st.columns([2, 3, 2])
                c1.markdown(f"**{record.get('repository_name', '—')}**")
                c2.markdown(f"_{record.get('request', '')[:60]}_")
                c3.markdown(f"`{record.get('timestamp', '')}`")
                with st.expander(f"View #{i + 1}", expanded=False):
                    url = record.get("repository_url", "")
                    if url:
                        st.markdown(f"🔗 [{url}]({url})")
                    intent_data = record.get("intent", {})
                    if intent_data:
                        st.json(intent_data)
                st.divider()


if __name__ == "__main__":
    main()
