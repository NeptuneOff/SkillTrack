from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings
from app.core.logging import log_event

logger = logging.getLogger("skilltrack.notifications")


def send_goal_completed_notification(recipient: str, display_name: str, skill: str) -> bool:
    """Envoie une notification non bloquante via le relais SMTP local MailHog."""
    message = EmailMessage()
    message["Subject"] = "Objectif SkillTrack terminé"
    message["From"] = "SkillTrack <noreply@skilltrack.local>"
    message["To"] = recipient
    message.set_content(
        f"Bonjour {display_name},\n\n"
        f"Bravo : votre objectif « {skill} » est maintenant terminé dans SkillTrack.\n\n"
        "L'équipe SkillTrack"
    )
    try:
        with smtplib.SMTP(settings.mailhog_host, settings.mailhog_port, timeout=3) as smtp:
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        log_event(
            logger,
            logging.WARNING,
            "goal_notification",
            status="failed",
            error_type=type(exc).__name__,
        )
        return False
    log_event(logger, logging.INFO, "goal_notification", status="sent")
    return True
