"""
Twilio notification service module.
Sends SMS and WhatsApp notifications on code generation events.
"""

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


class TwilioService:
    """Service layer for sending SMS and WhatsApp notifications via Twilio."""

    def __init__(self) -> None:
        self._enabled = bool(Config.TWILIO_ACCOUNT_SID and Config.TWILIO_AUTH_TOKEN)
        if self._enabled:
            self._client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
            logger.info("TwilioService initialized.")
        else:
            self._client = None
            logger.warning("TwilioService disabled: TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN missing.")

    def send_sms(self, message: str) -> bool:
        """
        Send an SMS notification.

        Args:
            message: Text message content to send.

        Returns:
            True if sent successfully, False otherwise.
        """
        if not self._enabled or not Config.ENABLE_SMS:
            logger.info("SMS notifications disabled. Skipping SMS.")
            return False

        if not Config.RECIPIENT_PHONE_NUMBER:
            logger.warning("RECIPIENT_PHONE_NUMBER not set. Skipping SMS.")
            return False

        try:
            msg = self._client.messages.create(
                body=message,
                from_=Config.TWILIO_PHONE_NUMBER,
                to=Config.RECIPIENT_PHONE_NUMBER,
            )
            logger.info("SMS sent | SID=%s | to=%s", msg.sid, Config.RECIPIENT_PHONE_NUMBER)
            return True
        except TwilioRestException as exc:
            logger.error("Twilio SMS error: %s", exc)
            return False
        except Exception as exc:
            logger.error("Unexpected SMS error: %s", exc, exc_info=True)
            return False

    def send_whatsapp(self, message: str) -> bool:
        """
        Send a WhatsApp notification.

        Args:
            message: Text message content to send.

        Returns:
            True if sent successfully, False otherwise.
        """
        if not self._enabled or not Config.ENABLE_WHATSAPP:
            logger.info("WhatsApp notifications disabled. Skipping WhatsApp.")
            return False

        if not Config.RECIPIENT_WHATSAPP_NUMBER:
            logger.warning("RECIPIENT_WHATSAPP_NUMBER not set. Skipping WhatsApp.")
            return False

        try:
            recipient = Config.RECIPIENT_WHATSAPP_NUMBER
            if not recipient.startswith("whatsapp:"):
                recipient = f"whatsapp:{recipient}"

            msg = self._client.messages.create(
                body=message,
                from_=Config.TWILIO_WHATSAPP_NUMBER,
                to=recipient,
            )
            logger.info("WhatsApp sent | SID=%s | to=%s", msg.sid, recipient)
            return True
        except TwilioRestException as exc:
            logger.error("Twilio WhatsApp error: %s", exc)
            return False
        except Exception as exc:
            logger.error("Unexpected WhatsApp error: %s", exc, exc_info=True)
            return False

    def notify_success(self, language: str, task: str, tokens: int) -> None:
        """
        Send success notification after code generation.

        Args:
            language: Programming language used.
            task: Short task description.
            tokens: Total tokens consumed.
        """
        task_preview = task[:80] + "..." if len(task) > 80 else task
        message = (
            f"✅ Code Generation Successful!\n"
            f"Language: {language.upper()}\n"
            f"Task: {task_preview}\n"
            f"Tokens used: {tokens}"
        )
        self.send_sms(message)
        self.send_whatsapp(message)

    def notify_error(self, language: str, error: str) -> None:
        """
        Send error notification on generation failure.

        Args:
            language: Programming language attempted.
            error: Error message to include.
        """
        message = (
            f"❌ Code Generation Failed!\n"
            f"Language: {language.upper()}\n"
            f"Error: {error[:120]}"
        )
        self.send_sms(message)
        self.send_whatsapp(message)
