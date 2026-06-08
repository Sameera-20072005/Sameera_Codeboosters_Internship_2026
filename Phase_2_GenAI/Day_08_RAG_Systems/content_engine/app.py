"""
Multi-Platform Content Engine — app.py
Streamlit entry point. Orchestrates all chains, services, and utilities.
"""

import streamlit as st
from dotenv import load_dotenv

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
    "LinkedIn":  {"key": "linkedin",  "icon": "💼"},
    "Instagram": {"key": "instagram", "icon": "📸"},
    "Facebook":  {"key": "facebook",  "icon": "👥"},
    "X (Twitter)": {"key": "twitter", "icon": "🐦"},
    "YouTube":   {"key": "youtube",   "icon": "▶️"},
}

LENGTHS  = ["Short", "Medium", "Long"]
TONES    = ["Professional", "Friendly", "Casual", "Humorous"]


# ── Service initialisation (cached) ──────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_services():
    """Initialise and cache all services for the app lifetime."""
    groq    = GroqService()
    history = HistoryService()
    export  = ExportService()
    chains  = {
        "linkedin":  LinkedInChain(groq),
        "instagram": InstagramChain(groq),
        "facebook":  FacebookChain(groq),
        "twitter":   TwitterChain(groq),
        "youtube":   YouTubeChain(groq),
    }
    return groq, history, export, chains


def run_chain(chains: dict, platform_key: str, topic: str, tone: str, length: str) -> str:
    """Dispatch generation to the correct platform chain."""
    return chains[platform_key].run(
        topic=topic,
        tone=tone.lower(),
        length=length.lower(),
    )


# ── Main app ──────────────────────────────────────────────────────────────────
def main() -> None:
    # Session state defaults
    if "generated_content" not in st.session_state:
        st.session_state.generated_content = ""
    if "last_record" not in st.session_state:
        st.session_state.last_record = {}

    # ── Service init ──────────────────────────────────────────────────────────
    try:
        groq_svc, history_svc, export_svc, chains = get_services()
    except EnvironmentError as exc:
        st.error(f"⚠️ Configuration error: {exc}")
        st.stop()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.title("✍️ Content Engine")
        st.markdown("---")

        platform_label = st.selectbox(
            "📱 Platform",
            options=list(PLATFORMS.keys()),
        )
        platform_key  = PLATFORMS[platform_label]["key"]
        platform_icon = PLATFORMS[platform_label]["icon"]

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

    # ── Input area ────────────────────────────────────────────────────────────
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
    if generate_clicked:
        if not topic.strip():
            st.warning("⚠️ Please enter a topic before generating.")
        else:
            logger.info(
                "Generate request | platform=%s | tone=%s | length=%s | topic=%s",
                platform_key, tone, length, topic[:80],
            )
            with st.spinner(f"Generating {platform_label} content..."):
                try:
                    content = run_chain(chains, platform_key, topic, tone, length)
                    st.session_state.generated_content = content

                    record = {
                        "platform": platform_label,
                        "topic": topic,
                        "tone": tone,
                        "length": length,
                        "content": content,
                    }
                    st.session_state.last_record = record

                    history_svc.save_content(
                        platform=platform_label,
                        topic=topic,
                        tone=tone,
                        length=length,
                        content=content,
                    )
                    logger.info("Content generated successfully | platform=%s", platform_key)

                except RuntimeError as exc:
                    st.error(f"❌ Generation failed: {exc}")
                    logger.error("Generation error: %s", exc)
                    st.stop()

    # ── Output area ───────────────────────────────────────────────────────────
    with col_output:
        st.subheader(f"{platform_icon} Generated Content")

        content = st.session_state.generated_content

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
                    data=export_svc.export_txt(content, platform_label, topic),
                    file_name=f"{platform_key}_content.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
            with e2:
                st.download_button(
                    "📋 Download JSON",
                    data=export_svc.export_json(record),
                    file_name=f"{platform_key}_content.json",
                    mime="application/json",
                    use_container_width=True,
                )
            with e3:
                history = history_svc.load_history()
                st.download_button(
                    "📊 Download CSV",
                    data=export_svc.export_csv(history),
                    file_name="content_history.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
        else:
            st.info("Generated content will appear here after you click Generate.")

    # ── History section ───────────────────────────────────────────────────────
    st.markdown("---")
    with st.expander("🕑 Generation History", expanded=False):
        history = history_svc.load_history()
        if not history:
            st.info("No history yet. Generate some content to see it here.")
        else:
            col_clear, _ = st.columns([1, 5])
            with col_clear:
                if st.button("🗑️ Clear History", type="secondary"):
                    history_svc.clear_history()
                    st.success("History cleared.")
                    st.rerun()

            for i, record in enumerate(history[:10]):
                with st.container():
                    h1, h2, h3 = st.columns([2, 2, 2])
                    h1.markdown(f"**{record.get('platform', '—')}**")
                    h2.markdown(f"_{record.get('topic', '')[:60]}_")
                    h3.markdown(f"`{record.get('timestamp', '')}`")
                    with st.expander(f"View content #{i + 1}"):
                        st.text(record.get("content", ""))
                    st.divider()


if __name__ == "__main__":
    main()
