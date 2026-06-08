"""
Prompt template module.
Builds structured, language-specific prompts for the LLM.
"""

from utils.logger import get_logger

logger = get_logger(__name__)

LANGUAGE_INSTRUCTIONS: dict[str, str] = {
    "python": (
        "Generate clean, optimized, and production-ready Python code for the following task.\n"
        "Requirements:\n"
        "- Follow PEP8 style guidelines\n"
        "- Add meaningful docstrings and inline comments\n"
        "- Use descriptive variable and function names\n"
        "- Use type hints where applicable\n"
        "- Handle edge cases and exceptions\n"
        "- Return ONLY the code block, no explanations outside the code"
    ),
    "javascript": (
        "Generate clean, optimized, and production-ready JavaScript code for the following task.\n"
        "Requirements:\n"
        "- Use modern ES6+ syntax (const/let, arrow functions, async/await)\n"
        "- Add JSDoc comments for functions\n"
        "- Use descriptive variable and function names\n"
        "- Handle errors using try/catch\n"
        "- Return ONLY the code block, no explanations outside the code"
    ),
    "sql": (
        "Generate a clean, optimized SQL query for the following task.\n"
        "Requirements:\n"
        "- Use standard SQL syntax compatible with PostgreSQL\n"
        "- Add inline comments explaining complex logic\n"
        "- Use meaningful table and column aliases\n"
        "- Optimize for readability and performance\n"
        "- Return ONLY the SQL query, no explanations outside the code"
    ),
}

SYSTEM_PROMPT = (
    "You are an expert software engineer and code generator. "
    "You produce only clean, working, well-commented code. "
    "Never include markdown fences (``` or ~~~) or prose explanations outside the code itself. "
    "Output only the raw code."
)


class PromptBuilder:
    """Builds LLM prompts based on language and user task."""

    @staticmethod
    def build(language: str, user_task: str) -> tuple[str, str]:
        """
        Build a system prompt and user prompt for the given language and task.

        Args:
            language: Target programming language ('python', 'javascript', 'sql').
            user_task: Plain-text description of what the code should do.

        Returns:
            Tuple of (system_prompt, user_prompt).

        Raises:
            ValueError: If language is not supported or task is empty.
        """
        language = language.strip().lower()
        user_task = user_task.strip()

        if not user_task:
            raise ValueError("Task description cannot be empty.")

        instructions = LANGUAGE_INSTRUCTIONS.get(language)
        if not instructions:
            supported = ", ".join(LANGUAGE_INSTRUCTIONS.keys())
            raise ValueError(f"Unsupported language '{language}'. Supported: {supported}")

        user_prompt = f"{instructions}\n\nTask:\n{user_task}"

        logger.info("Prompt built | language=%s | task_length=%d chars", language, len(user_task))
        return SYSTEM_PROMPT, user_prompt

    @staticmethod
    def supported_languages() -> list[str]:
        """Return list of supported language keys."""
        return list(LANGUAGE_INSTRUCTIONS.keys())
