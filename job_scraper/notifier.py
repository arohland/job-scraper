import smtplib, ssl
from email.mime.text import MIMEText
from typing import Union, List

from .logger import get_logger

logger = get_logger(__name__)

def send_email(config, subject: str, body: str) -> bool:
    recipients: Union[str, List[str]] = config["email"]["to"]
    if isinstance(recipients, str):
        recipients = [recipients]  # normalize

    msg = MIMEText(body, "plain")
    msg["Subject"] = subject
    msg["From"] = config["email"]["from"]
    msg["To"] = ", ".join(recipients)

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(config["email"]["smtp_server"], config["email"]["smtp_port"]) as server:
            server.starttls(context=context)
            server.login(config["email"]["username"], config["email"]["password"])
            server.send_message(msg)
        logger.info(f"Email sent successfully to {recipients}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}", exc_info=True)
        return False
