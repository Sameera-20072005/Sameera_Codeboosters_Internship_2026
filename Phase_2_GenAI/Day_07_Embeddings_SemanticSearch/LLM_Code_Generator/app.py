"""
Main Flask application entry point.
LLM-Powered Code Generator with Notifications.
"""

from flask import Flask, render_template, request, jsonify
from config import Config
from services.llm_service import LLMService
from services.twilio_service import TwilioService
from services.prompt_template import PromptBuilder
from utils.logger import get_logger

logger = get_logger(__name__)

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# Initialise services once at startup
try:
    llm_service = LLMService()
except EnvironmentError as e:
    logger.critical("Failed to initialise LLMService: %s", e)
    llm_service = None

twilio_service = TwilioService()


@app.route("/")
def index():
    """Render the main UI page."""
    missing = Config.validate()
    return render_template(
        "index.html",
        languages=PromptBuilder.supported_languages(),
        config_warnings=missing,
    )


@app.route("/generate", methods=["POST"])
def generate():
    """
    Handle code generation requests.

    Expected JSON body:
        {
            "language": "python" | "javascript" | "sql",
            "task": "Description of what to generate"
        }

    Returns:
        JSON response with generated code, token usage, and status.
    """
    data = request.get_json(silent=True) or {}
    language = (data.get("language") or "").strip().lower()
    task = (data.get("task") or "").strip()

    logger.info("Generate request | language=%s | task_length=%d", language, len(task))

    # --- Input validation ---
    if not language:
        return jsonify({"success": False, "error": "Please select a programming language."}), 400

    if not task:
        return jsonify({"success": False, "error": "Please enter a task description."}), 400

    if len(task) > 2000:
        return jsonify({"success": False, "error": "Task description is too long (max 2000 chars)."}), 400

    if llm_service is None:
        return jsonify({"success": False, "error": "LLM service unavailable. Check GROQ_API_KEY."}), 503

    # --- Build prompt ---
    try:
        system_prompt, user_prompt = PromptBuilder.build(language, task)
    except ValueError as exc:
        logger.warning("Prompt build error: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 400

    # --- Generate code ---
    try:
        generated_code, token_usage = llm_service.generate_code(system_prompt, user_prompt)

        # Send success notification (non-blocking; errors are logged internally)
        twilio_service.notify_success(language, task, token_usage.total_tokens)

        logger.info("Generation complete | language=%s | tokens=%d", language, token_usage.total_tokens)

        return jsonify({
            "success": True,
            "code": generated_code,
            "language": language,
            "token_usage": token_usage.to_dict(),
        })

    except RuntimeError as exc:
        error_msg = str(exc)
        logger.error("Generation failed: %s", error_msg)
        twilio_service.notify_error(language, error_msg)
        return jsonify({"success": False, "error": error_msg}), 500

    except Exception as exc:
        error_msg = f"Unexpected server error: {exc}"
        logger.error(error_msg, exc_info=True)
        twilio_service.notify_error(language, error_msg)
        return jsonify({"success": False, "error": "An unexpected error occurred. Please try again."}), 500


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "llm_ready": llm_service is not None,
        "model": Config.GROQ_MODEL,
    })


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found."}), 404


@app.errorhandler(500)
def server_error(e):
    logger.error("Unhandled 500 error: %s", e)
    return jsonify({"error": "Internal server error."}), 500


if __name__ == "__main__":
    logger.info("Starting LLM Code Generator app...")
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=5000)
