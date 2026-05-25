"""Feedback notification service.
Logs feedback to a local file and sends email notification
via Gmail SMTP (App Password)."""

import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText

# Feedback log file path
FEEDBACK_LOG_DIR = "data"
FEEDBACK_LOG_FILE = os.path.join(FEEDBACK_LOG_DIR, "feedback.log")

# Email configuration from environment
GMAIL_USER = os.environ.get("GMAIL_USER", "p94126541@gmail.com")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
FEEDBACK_RECIPIENT = os.environ.get("FEEDBACK_RECIPIENT", GMAIL_USER)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def send_email(to: str, subject: str, body: str) -> bool:
    """Send an email via Gmail SMTP. Returns True on success."""
    if not GMAIL_APP_PASSWORD:
        print("GMAIL_APP_PASSWORD not set. Skipping feedback email.")
        return False

    msg = MIMEText(body, "plain", "utf-8")
    msg["From"] = GMAIL_USER
    msg["To"] = to
    msg["Subject"] = subject

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send feedback email: {e}")
        return False


def log_feedback(category: str, message: str) -> None:
    """Persist feedback to a local log file (always, as fallback)."""
    os.makedirs(FEEDBACK_LOG_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = (
        f"[{timestamp}]\n"
        f"Category: {category}\n"
        f"Message: {message}\n"
        f"{'-' * 40}\n"
    )
    with open(FEEDBACK_LOG_FILE, "a") as f:
        f.write(entry)


def send_feedback_email(category: str, message: str) -> bool:
    """Attempt to send feedback via SMTP. Returns True on success."""
    body = (
        f"Category: {category}\n\n"
        f"Message:\n{message}\n"
    )
    return send_email(
        to=FEEDBACK_RECIPIENT,
        subject=f"[Feedback] {category}",
        body=body,
    )


def notify_feedback(category: str, message: str) -> None:
    """Process feedback notification: log locally, then attempt email."""
    # Always persist to local file first (safe fallback)
    log_feedback(category, message)

    # Attempt email notification
    success = send_feedback_email(category, message)
    if success:
        print(f"Feedback email sent: [{category}] {message[:50]}...")
    else:
        print(f"Feedback logged locally (email failed): [{category}] {message[:50]}...")