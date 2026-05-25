"""Feedback notification service.
Logs feedback to a local file and attempts to send email notification
using the existing gmcli integration."""

import os
import subprocess
from datetime import datetime

# Feedback log file path
FEEDBACK_LOG_DIR = "data"
FEEDBACK_LOG_FILE = os.path.join(FEEDBACK_LOG_DIR, "feedback.log")

# Default sender Gmail address (reused from notifier.py)
GMAIL_USER = "p94126541@gmail.com"
# Where to send feedback notifications
FEEDBACK_RECIPIENT = "p94126541@gmail.com"


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
    """Attempt to send feedback via gmcli. Returns True on success."""
    body = (
        f"Category: {category}\n\n"
        f"Message:\n{message}\n"
    )
    try:
        subprocess.run(
            [
                "gmcli", GMAIL_USER, "send",
                "--to", FEEDBACK_RECIPIENT,
                "--subject", f"[Feedback] {category}",
                "--body", body,
            ],
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Failed to send feedback email: {e}")
        return False


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