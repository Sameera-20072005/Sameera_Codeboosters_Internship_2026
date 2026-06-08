"""
Application configuration module.
Loads and validates all environment variables.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Central configuration class for the application."""

    # Flask
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-prod")
    DEBUG: bool = os.getenv("FLASK_DEBUG", "False").lower() == "true"

    # Groq
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # Twilio
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")
    TWILIO_WHATSAPP_NUMBER: str = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
    RECIPIENT_PHONE_NUMBER: str = os.getenv("RECIPIENT_PHONE_NUMBER", "")
    RECIPIENT_WHATSAPP_NUMBER: str = os.getenv("RECIPIENT_WHATSAPP_NUMBER", "")

    # Notifications
    ENABLE_SMS: bool = os.getenv("ENABLE_SMS", "False").lower() == "true"
    ENABLE_WHATSAPP: bool = os.getenv("ENABLE_WHATSAPP", "False").lower() == "true"

    # Logging
    LOG_FILE: str = os.path.join(os.path.dirname(__file__), "logs", "app.log")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls) -> list[str]:
        """Return list of missing required config keys."""
        missing = []
        if not cls.GROQ_API_KEY:
            missing.append("GROQ_API_KEY")
        return missing
