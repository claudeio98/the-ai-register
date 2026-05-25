import subprocess
import sqlite3
from db import get_connection

# Default sender Gmail address (used as the "from" address for gmcli)
GMAIL_USER = "p94126541@gmail.com"

def get_active_subscribers():
    """Fetch all active subscriber email addresses."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM subscribers WHERE active = 1")
        return [row[0] for row in cursor.fetchall()]

def generate_digest():
    """Build a digest of high-value events that haven't been notified yet."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, title, speaker, institution, date, url, score 
            FROM events 
            WHERE score >= 7 AND status = 'discovered'
            ORDER BY score DESC
        ''')
        high_value_events = cursor.fetchall()
        
    if not high_value_events:
        print("No high-value events to notify.")
        return None, []

    digest = "AI Events Intelligence Digest\n"
    digest += "==============================\n\n"
    
    event_ids = []
    for event in high_value_events:
        eid, title, speaker, inst, date, url, score = event
        event_ids.append(eid)
        digest += f"Score: {score}/10\n"
        digest += f"Title: {title}\n"
        digest += f"Speaker: {speaker if speaker else 'N/A'}\n"
        digest += f"Institution: {inst if inst else 'N/A'}\n"
        digest += f"Date: {date if date else 'TBD'}\n"
        digest += f"URL: {url}\n"
        digest += "------------------------------\n"
    
    return digest, event_ids

def mark_events_notified(event_ids):
    """Mark events as notified and log to notifications table."""
    with get_connection() as conn:
        cursor = conn.cursor()
        for eid in event_ids:
            cursor.execute("UPDATE events SET status = 'notified' WHERE id = ?", (eid,))
            cursor.execute("INSERT INTO notifications (event_id) VALUES (?)", (eid,))
        conn.commit()

def send_notifications():
    digest, event_ids = generate_digest()
    if not digest:
        return

    subscribers = get_active_subscribers()
    if not subscribers:
        print("No active subscribers. Skipping notification send.")
        return

    print(f"Sending email digest to {len(subscribers)} subscriber(s)...")
    success_count = 0
    fail_count = 0

    for email in subscribers:
        try:
            subprocess.run([
                "gmcli", GMAIL_USER, "send",
                "--to", email,
                "--subject", "🚀 AI Events Intelligence Digest",
                "--body", digest
            ], check=True)
            print(f"  ✓ Sent to {email}")
            success_count += 1
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Failed to send to {email}: {e}")
            fail_count += 1

    if success_count > 0 and event_ids:
        mark_events_notified(event_ids)
        print(f"Notifications sent successfully to {success_count} subscriber(s).")
    if fail_count > 0:
        print(f"Failed to send to {fail_count} subscriber(s).")

if __name__ == "__main__":
    send_notifications()