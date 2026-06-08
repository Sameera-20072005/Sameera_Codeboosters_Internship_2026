"""
Centralised prompt templates for all supported social media platforms.
Each template encodes the platform persona, tone, and structural requirements.

Uses langchain_core.prompts (LangChain >=0.2 compatible).
"""

from langchain_core.prompts import PromptTemplate

# ── LinkedIn ──────────────────────────────────────────────────────────────────
LINKEDIN_TEMPLATE = PromptTemplate(
    input_variables=["topic", "tone", "length"],
    template=(
        "You are a professional LinkedIn content creator with expertise in business and industry trends.\n\n"
        "Create a {length} LinkedIn post about: {topic}\n\n"
        "Tone: {tone}\n\n"
        "Requirements:\n"
        "- Start with a compelling hook or insight\n"
        "- Use industry-focused, professional language\n"
        "- Include a clear call-to-action at the end\n"
        "- Add 3-5 relevant professional hashtags\n"
        "- Use line breaks for readability\n"
        "- No markdown formatting symbols\n\n"
        "Generate the LinkedIn post now:"
    ),
)

# ── Instagram ─────────────────────────────────────────────────────────────────
INSTAGRAM_TEMPLATE = PromptTemplate(
    input_variables=["topic", "tone", "length"],
    template=(
        "You are a creative Instagram content creator who crafts engaging, visually-descriptive captions.\n\n"
        "Create a {length} Instagram caption about: {topic}\n\n"
        "Tone: {tone}\n\n"
        "Requirements:\n"
        "- Start with an attention-grabbing first line\n"
        "- Use emojis naturally throughout the caption\n"
        "- Keep the style casual and relatable\n"
        "- Include a question or CTA to boost engagement\n"
        "- End with 10-15 relevant hashtags on a new line\n"
        "- No markdown formatting symbols\n\n"
        "Generate the Instagram caption now:"
    ),
)

# ── Facebook ──────────────────────────────────────────────────────────────────
FACEBOOK_TEMPLATE = PromptTemplate(
    input_variables=["topic", "tone", "length"],
    template=(
        "You are a Facebook community manager who creates warm, engaging posts that spark conversations.\n\n"
        "Create a {length} Facebook post about: {topic}\n\n"
        "Tone: {tone}\n\n"
        "Requirements:\n"
        "- Write in a friendly, community-oriented voice\n"
        "- Encourage comments and discussion\n"
        "- Use relatable language and occasional emojis\n"
        "- Include a question at the end to drive engagement\n"
        "- Add 3-5 relevant hashtags\n"
        "- No markdown formatting symbols\n\n"
        "Generate the Facebook post now:"
    ),
)

# ── X / Twitter ───────────────────────────────────────────────────────────────
TWITTER_TEMPLATE = PromptTemplate(
    input_variables=["topic", "tone", "length"],
    template=(
        "You are a sharp X (Twitter) content creator who writes concise, high-impact tweets.\n\n"
        "Create a {length} tweet about: {topic}\n\n"
        "Tone: {tone}\n\n"
        "Requirements:\n"
        "- Keep it under 280 characters if short, up to 500 if medium/long thread\n"
        "- Be direct, punchy, and shareable\n"
        "- Use trending language and style\n"
        "- Include 2-3 relevant hashtags\n"
        "- No markdown formatting symbols\n\n"
        "Generate the tweet now:"
    ),
)

# ── YouTube ───────────────────────────────────────────────────────────────────
YOUTUBE_TEMPLATE = PromptTemplate(
    input_variables=["topic", "tone", "length"],
    template=(
        "You are a YouTube SEO and content specialist who crafts optimised video titles and descriptions.\n\n"
        "Create YouTube content for a {length} video about: {topic}\n\n"
        "Tone: {tone}\n\n"
        "Requirements:\n"
        "- Write a click-worthy, SEO-optimised video TITLE (max 70 characters)\n"
        "- Write a detailed video DESCRIPTION (150-300 words)\n"
        "  - First 2 sentences must hook the viewer\n"
        "  - Include timestamps placeholder section\n"
        "  - Include a subscribe CTA\n"
        "- End with 10-15 relevant hashtags\n"
        "- No markdown formatting symbols\n\n"
        "Generate the YouTube title, description, and hashtags now:"
    ),
)

PLATFORM_TEMPLATES: dict[str, PromptTemplate] = {
    "linkedin":  LINKEDIN_TEMPLATE,
    "instagram": INSTAGRAM_TEMPLATE,
    "facebook":  FACEBOOK_TEMPLATE,
    "twitter":   TWITTER_TEMPLATE,
    "youtube":   YOUTUBE_TEMPLATE,
}


def sanitise_topic(topic: str) -> str:
    """
    Escape curly braces in user-supplied topic so they don't
    break PromptTemplate variable substitution.

    Args:
        topic: Raw user input string.

    Returns:
        Topic with literal braces escaped.
    """
    return topic.replace("{", "{{").replace("}", "}}")
