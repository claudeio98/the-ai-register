"""Notification service using Gmail SMTP (App Password).
Sends HTML-formatted email digests of high-value events to subscribers,
and handles feedback email notifications."""

import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from db import get_connection

# Email configuration from environment
GMAIL_USER = os.environ.get("GMAIL_USER", "theairegister@gmail.com")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
FEEDBACK_RECIPIENT = os.environ.get("FEEDBACK_RECIPIENT", GMAIL_USER)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Feedback log file path
FEEDBACK_LOG_DIR = "data"
FEEDBACK_LOG_FILE = os.path.join(FEEDBACK_LOG_DIR, "feedback.log")


def send_email(to: str, subject: str, html_body: str, text_body: str | None = None) -> bool:
    """Send a multipart (HTML + plain text) email via Gmail SMTP. Returns True on success."""
    if not GMAIL_APP_PASSWORD:
        print("GMAIL_APP_PASSWORD not set. Skipping email.")
        return False

    msg = MIMEMultipart("alternative")
    msg["From"] = GMAIL_USER
    msg["To"] = to
    msg["Subject"] = subject

    # Plain text fallback
    if text_body:
        msg.attach(MIMEText(text_body, "plain", "utf-8"))

    # HTML version
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send email to {to}: {e}")
        return False


def get_active_subscribers():
    """Fetch all active subscriber email addresses."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM subscribers WHERE active = 1")
        return [row[0] for row in cursor.fetchall()]


def _build_html_digest(events: list[tuple]) -> str:
    """Build an HTML-formatted digest from a list of event tuples."""
    cards_html = ""
    for event in events:
        eid, title, speaker, inst, date, url, score = event
        score_pct = int(score)  # e.g. 9/10 → 90%
        score_color = "#22c55e" if score >= 8 else "#eab308"  # green / yellow

        # Rating stars
        stars = "★" * (score_pct // 2) + "☆" * (5 - score_pct // 2)
        stars_colored = ""
        for i, s in enumerate(stars):
            if i < score_pct // 2:
                stars_colored += f'<span style="color:{score_color}">★</span>'
            else:
                stars_colored += f'<span style="color:#4b5563">☆</span>'

        institution_html = (
            f'<span style="color:#9ca3af"> {inst}</span>'
            if inst else ""
        )
        date_display = date if date else "TBA"
        speaker_display = speaker if speaker else None

        cards_html += f"""
        <tr>
            <td style="padding:0 0 20px 0">
                <table cellpadding="0" cellspacing="0" style="width:100%;background:#1f2937;border-radius:12px;border:1px solid #374151">
                    <tr>
                        <td style="padding:20px">
                            <!-- Score badge + stars -->
                            <table cellpadding="0" cellspacing="0" style="width:100%">
                                <tr>
                                    <td style="vertical-align:middle">
                                        <span style="display:inline-block;background:{score_color};color:#0f172a;font-size:13px;font-weight:700;padding:4px 10px;border-radius:6px">{score}/10</span>
                                        <span style="margin-left:8px;font-size:15px">{stars_colored}</span>
                                    </td>
                                    <td style="text-align:right;vertical-align:middle">
                                        <a href="{url}" style="color:#60a5fa;text-decoration:none;font-size:13px;font-weight:600">View Event →</a>
                                    </td>
                                </tr>
                            </table>

                            <!-- Title -->
                            <p style="margin:12px 0 8px 0;font-size:17px;font-weight:600;color:#f3f4f6;line-height:1.4">{title}</p>

                            <!-- Speaker & Institution -->
                            <p style="margin:0 0 4px 0;font-size:14px;color:#d1d5db">
                                {"🎤 " + speaker_display if speaker_display else ""}
                                {institution_html}
                            </p>

                            <!-- Date -->
                            <p style="margin:4px 0 0 0;font-size:14px;color:#9ca3af">📅 {date_display}</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background-color:#0f172a;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif">
    <table cellpadding="0" cellspacing="0" style="width:100%;max-width:600px;margin:0 auto;background-color:#0f172a">
        <tr>
            <td style="padding:40px 24px 0 24px">
                <!-- Header banner -->
                <table cellpadding="0" cellspacing="0" style="width:100%;background:linear-gradient(135deg,#1e3a5f,#312e81);border-radius:16px">
                    <tr>
                        <td style="padding:30px 24px;text-align:center">
                            <p style="margin:0;font-size:42px;line-height:1">🚀</p>
                            <h1 style="margin:12px 0 4px 0;font-size:24px;font-weight:700;color:#f8fafc">London AI Radar</h1>
                            <p style="margin:0 0 12px 0;font-size:15px;color:#94a3b8">Your weekly AI events intelligence</p>
                            <span style="display:inline-block;background:rgba(255,255,255,0.15);color:#f8fafc;font-size:14px;padding:6px 16px;border-radius:20px">
                                {len(events)} new high-value event{'' if len(events) == 1 else 's'} found
                            </span>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        <tr>
            <td style="padding:24px 24px 0 24px">
                <p style="margin:0 0 20px 0;font-size:15px;color:#94a3b8;line-height:1.5">
                    Here are the top AI events, conferences, and talks hand-picked for you this week.
                </p>
            </td>
        </tr>
        <tr>
            <td style="padding:0 24px">
                <table cellpadding="0" cellspacing="0" style="width:100%">
                    {cards_html}
                </table>
            </td>
        </tr>
        <!-- Footer -->
        <tr>
            <td style="padding:20px 24px 40px 24px">
                <table cellpadding="0" cellspacing="0" style="width:100%">
                    <tr>
                        <td style="border-top:1px solid #1f2937;padding:20px 0 0 0;text-align:center">
                            <p style="margin:0;font-size:12px;color:#6b7280">
                                You're receiving this because you subscribed to London AI Radar.
                            </p>
                            <p style="margin:8px 0 0 0;font-size:12px;color:#6b7280">
                                Powered by <a href="https://github.com" style="color:#60a5fa;text-decoration:none">AI Events Tracker</a>
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""
    return html


def _build_text_digest(events: list[tuple]) -> str:
    """Build a plain-text digest as fallback for HTML users."""
    lines = ["🚀 LONDON AI RADAR — AI Events Intelligence Digest", "=" * 48, ""]
    lines.append(f"{len(events)} new high-value event{'s' if len(events) > 1 else ''} found")
    lines.append("")

    for event in events:
        eid, title, speaker, inst, date, url, score = event
        lines.append(f"⭐ {'★' * (int(score) // 2)}{'☆' * (5 - int(score) // 2)}  Score: {score}/10")
        lines.append(f"   {title}")
        if speaker:
            lines.append(f"   🎤 {speaker}{' · ' + inst if inst else ''}")
        elif inst:
            lines.append(f"   🏛 {inst}")
        lines.append(f"   📅 {date if date else 'TBA'}")
        lines.append(f"   🔗 {url}")
        lines.append("")

    lines.append("-" * 48)
    lines.append("You're receiving this because you subscribed to London AI Radar.")
    lines.append("")
    return "\n".join(lines)


def _is_future_date(date_str: str | None, today: datetime) -> bool:
    """Check if a date string represents today or a future date.

    Handles multiple formats stored in the DB: YYYY, YYYY-MM, YYYY-MM-DD.
    Events with no date are included (we can't rule them out).
    """
    if not date_str:
        return True
    parts = date_str.split("-")
    if len(parts) == 1 and len(parts[0]) == 4:
        return int(parts[0]) >= today.year
    if len(parts) == 2:
        return (int(parts[0]), int(parts[1])) >= (today.year, today.month)
    if len(parts) == 3:
        return date_str >= today.strftime("%Y-%m-%d")
    return True


def generate_digest():
    """Fetch high-value future events and return (html_digest, text_digest, event_ids)."""
    today = datetime.now()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, title, speaker, institution, date, url, score
            FROM events
            WHERE score >= 7 AND status = 'discovered'
              AND (date >= date('now') OR date IS NULL OR date NOT GLOB '____-__-__')
            ORDER BY score DESC
        ''')
        all_high_value = cursor.fetchall()

    # Python post-filter for non-standard date formats (YYYY, YYYY-MM)
    high_value_events = [e for e in all_high_value if _is_future_date(e[4], today)]

    if not high_value_events:
        print("No high-value events to notify.")
        return None, None, []

    event_ids = [e[0] for e in high_value_events]
    html_digest = _build_html_digest(high_value_events)
    text_digest = _build_text_digest(high_value_events)
    return html_digest, text_digest, event_ids


def mark_events_notified(event_ids):
    """Mark events as notified and log to notifications table."""
    with get_connection() as conn:
        cursor = conn.cursor()
        for eid in event_ids:
            cursor.execute("UPDATE events SET status = 'notified' WHERE id = ?", (eid,))
            cursor.execute("INSERT INTO notifications (event_id) VALUES (?)", (eid,))
        conn.commit()


def send_notifications():
    html_digest, text_digest, event_ids = generate_digest()
    if not html_digest:
        return

    subscribers = get_active_subscribers()
    if not subscribers:
        print("No active subscribers. Skipping notification send.")
        return

    print(f"Sending email digest to {len(subscribers)} subscriber(s)...")
    success_count = 0
    fail_count = 0

    for email in subscribers:
        if send_email(
            to=email,
            subject="🚀 London AI Radar — AI Events Intelligence Digest",
            html_body=html_digest,
            text_body=text_digest,
        ):
            print(f"  ✓ Sent to {email}")
            success_count += 1
        else:
            print(f"  ✗ Failed to send to {email}")
            fail_count += 1

    if success_count > 0 and event_ids:
        mark_events_notified(event_ids)
        print(f"Notifications sent successfully to {success_count} subscriber(s).")
    if fail_count > 0:
        print(f"Failed to send to {fail_count} subscriber(s).")


# --- Feedback notification ---

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
    """Send a plain-text feedback email via Gmail SMTP. Returns True on success."""
    body = (
        f"Category: {category}\n\n"
        f"Message:\n{message}\n"
    )
    return send_email(
        to=FEEDBACK_RECIPIENT,
        subject=f"[Feedback] {category}",
        html_body=body,
        text_body=body,
    )


def notify_feedback(category: str, message: str) -> None:
    """Process feedback notification: log locally, then attempt email."""
    log_feedback(category, message)
    success = send_feedback_email(category, message)
    if success:
        print(f"Feedback email sent: [{category}] {message[:50]}...")
    else:
        print(f"Feedback logged locally (email failed): [{category}] {message[:50]}...")


if __name__ == "__main__":
    send_notifications()