"""
Multi-Platform Content Engine — app.py
Streamlit entry point. Orchestrates all chains, services, and utilities.
"""

import sys
import os
import streamlit as st
from typing import NamedTuple
from dotenv import load_dotenv

# ── sys.path guard: ensure package root is on the path regardless of CWD ──────
_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from services.groq_service import GroqService
from services.history_service import HistoryService
from services.export_service import ExportService
from chains.linkedin_chain import LinkedInChain
from chains.instagram_chain import InstagramChain
from chains.facebook_chain import FacebookChain
from chains.twitter_chain import TwitterChain
from chains.youtube_chain import YouTubeChain
from utils.analytics import analyse
from utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Multi-Platform Content Engine",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Platform metadata ─────────────────────────────────────────────────────────
PLATFORMS: dict[str, dict] = {
    "LinkedIn":    {"key": "linkedin",  "icon": "💼"},
    "Instagram":   {"key": "instagram", "icon": "📸"},
    "Facebook":    {"key": "facebook",  "icon": "👥"},
    "X (Twitter)": {"key": "twitter",   "icon": "🐦"},
    "YouTube":     {"key": "youtube",   "icon": "▶️"},
}

LENGTHS = ["Short", "Medium", "Long"]
TONES   = ["Professional", "Friendly", "Casual", "Humorous"]


# ── Services container (NamedTuple avoids multi-value return pitfalls) ────────
class AppServices(NamedTuple):
    groq:    GroqService
    history: HistoryService
    export:  ExportService
    chains:  dict


@st.cache_resource(show_spinner=False)
def _init_services() -> AppServices | None:
    """
    Initialise and cache all services for the app lifetime.
    Returns None if EnvironmentError is raised (missing API key).
    """
    try:
        groq    = GroqService()
        history = HistoryService()
        export  = ExportService()
        chains: dict = {
            "linkedin":  LinkedInChain(groq),
            "instagram": InstagramChain(groq),
            "facebook":  FacebookChain(groq),
            "twitter":   TwitterChain(groq),
            "youtube":   YouTubeChain(groq),
        }
        return AppServices(groq=groq, history=history, export=export, chains=chains)
    except EnvironmentError as exc:
        logger.critical("Service init failed: %s", exc)
        return None


# ── Main app ──────────────────────────────────────────────────────────────────
def main() -> None:
    # ── Service init — checked OUTSIDE cache so errors display properly ───────
    svc = _init_services()
    if svc is None:
        st.error(
            "⚠️ **Configuration error:** `GROQ_API_KEY` is missing or invalid.\n\n"
            "Add it to your `.env` file and restart the app."
        )
        st.stop()

    # ── Session state defaults ────────────────────────────────────────────────
    if "generated_content" not in st.session_state:
        st.session_state.generated_content = ""
    if "last_record" not in st.session_state:
        st.session_state.last_record = {}
    if "current_topic" not in st.session_state:
        st.session_state.current_topic = ""

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.title("✍️ Content Engine")
        st.markdown("---")

        platform_label = st.selectbox("📱 Platform", options=list(PLATFORMS.keys()))
        platform_key   = PLATFORMS[platform_label]["key"]
        platform_icon  = PLATFORMS[platform_label]["icon"]

        length = st.selectbox("📏 Content Length", LENGTHS, index=1)
        tone   = st.selectbox("🎭 Tone", TONES, index=0)

        st.markdown("---")
        st.caption("Powered by Groq · LLaMA 3.3 · LangChain")

    # ── Main header ───────────────────────────────────────────────────────────
    st.title("🚀 Multi-Platform Content Engine")
    st.markdown(
        f"Generate **{platform_icon} {platform_label}** content — "
        f"tone: **{tone}** | length: **{length}**"
    )
    st.markdown("---")

    # ── Input / Output columns ────────────────────────────────────────────────
    col_input, col_output = st.columns([1, 1], gap="large")

    with col_input:
        st.subheader("📝 Topic Input")
        topic = st.text_area(
            "Enter your topic or idea",
            placeholder="e.g. The impact of AI on the future of remote work",
            height=160,
            max_chars=500,
        )
        st.caption(f"{len(topic)} / 500 characters")

        generate_clicked = st.button(
            f"⚡ Generate {platform_label} Content",
            type="primary",
            use_container_width=True,
        )

    # ── Generation logic ──────────────────────────────────────────────────────
    # Runs outside col_output so errors display full-width before the output col renders
    if generate_clicked:
        if not topic.strip():
            st.warning("⚠️ Please enter a topic before generating.")
        else:
            logger.info(
                "Generate request | platform=%s | tone=%s | length=%s | topic=%.80s",
                platform_key, tone, length, topic,
            )
            error_placeholder = st.empty()
            with st.spinner(f"Generating {platform_label} content..."):
                try:
                    content = svc.chains[platform_key].run(
                        topic=topic, tone=tone.lower(), length=length.lower()
                    )
                    st.session_state.generated_content = content
                    st.session_state.current_topic = topic
                    st.session_state.last_record = {
                        "platform": platform_label,
                        "topic": topic,
                        "tone": tone,
                        "length": length,
                        "content": content,
                    }
                    svc.history.save_content(
                        platform=platform_label,
                        topic=topic,
                        tone=tone,
                        length=length,
                        content=content,
                    )
                    logger.info("Content generated successfully | platform=%s", platform_key)

                except (RuntimeError, ValueError) as exc:
                    # Display error outside spinner — avoids StopException swallowing it
                    error_placeholder.error(f"❌ Generation failed: {exc}")
                    logger.error("Generation error: %s", exc)
                    st.session_state.generated_content = ""

    # ── Output area ───────────────────────────────────────────────────────────
    with col_output:
        st.subheader(f"{platform_icon} Generated Content")
        content = st.session_state.generated_content
        # Use persisted topic so it's always available in the output column
        saved_topic = st.session_state.get("current_topic", "")

        if content:
            st.text_area(
                "Output",
                value=content,
                height=320,
                label_visibility="collapsed",
            )

            # ── Analytics ─────────────────────────────────────────────────────
            st.markdown("#### 📊 Content Analytics")
            stats = analyse(content)
            a1, a2, a3, a4 = st.columns(4)
            a1.metric("Words",      stats.word_count)
            a2.metric("Characters", stats.char_count)
            a3.metric("Sentences",  stats.sentence_count)
            a4.metric("Hashtags",   stats.hashtag_count)

            # ── Export buttons ────────────────────────────────────────────────
            st.markdown("#### 💾 Export")
            record = st.session_state.last_record
            e1, e2, e3 = st.columns(3)

            with e1:
                st.download_button(
                    "📄 Download TXT",
                    data=svc.export.export_txt(content, platform_label, saved_topic),
                    file_name=f"{platform_key}_content.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
            with e2:
                st.download_button(
                    "📋 Download JSON",
                    data=svc.export.export_json(record),
                    file_name=f"{platform_key}_content.json",
                    mime="application/json",
                    use_container_width=True,
                )
            with e3:
                st.download_button(
                    "📊 Download CSV",
                    data=svc.export.export_csv(svc.history.load_history()),
                    file_name="content_history.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
        else:
            st.info("Generated content will appear here after you click Generate.")

    # ── History section ───────────────────────────────────────────────────────
    st.markdown("---")
    with st.expander("🕑 Generation History", expanded=False):
        history = svc.history.load_history()
        if not history:
            st.info("No history yet. Generate some content to see it here.")
        else:
            # Single clear button outside the loop to avoid duplicate widget keys
            if st.button("🗑️ Clear History", type="secondary", key="clear_history_btn"):
                svc.history.clear_history()
                st.session_state.generated_content = ""
                st.session_state.last_record = {}
                st.session_state.current_topic = ""
                st.success("History cleared.")
                st.rerun()

            for i, record in enumerate(history[:10]):
                h1, h2, h3 = st.columns([2, 3, 2])
                h1.markdown(f"**{record.get('platform', '—')}**")
                h2.markdown(f"_{record.get('topic', '')[:60]}_")
                h3.markdown(f"`{record.get('timestamp', '')}`")
                with st.expander(f"View content #{i + 1}", expanded=False):
                    st.text(record.get("content", ""))
                st.divider()


if __name__ == "__main__":
    main()
