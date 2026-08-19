import logging
import smtplib
from email.message import EmailMessage

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class EmailService:
    def send_welcome_email(self, recipient: str, display_name: str) -> bool:
        settings = get_settings()
        message = EmailMessage()
        message["Subject"] = "Bienvenue sur SkillTrack"
        message["From"] = settings.mail_from
        message["To"] = recipient
        message.set_content(
            f"Bonjour {display_name},\n\nVotre compte SkillTrack est prêt.\n"
            "Ce message est envoyé via le service SMTP de test MailHog.\n"
        )
        try:
            with smtplib.SMTP(settings.mail_host, settings.mail_port, timeout=5) as smtp:
                smtp.send_message(message)
            return True
        except OSError as exc:
            logger.warning("welcome_email_not_sent", extra={"recipient": recipient, "error": str(exc)})
            return False
