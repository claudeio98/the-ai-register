import subprocess
import sqlite3
from db import get_connection

# Your Gmail address (could be moved to an environment variable)
GMAIL_USER = "p94126541@gmail.com"

def generate_digest():
    with get_connection() as conn:
        cursor = conn.cursor()
        # Get events that are high score and not notified
        cursor.execute('''
            SELECT id, title, speaker, institution, date, url, score 
            FROM events 
            WHERE score >= 7 AND status = 'discovered'
            ORDER BY score DESC
        ''')
        high_value_events = cursor.fetchall()
        
    if not high_value_events:
        print("No high-value events to notify.")
        return None

    digest = "AI Events Intelligence Digest\n"
    digest += "==============================\n\n"
    
    for event in high_value_events:
        eid, title, speaker, inst, date, url, score = event
        digest += f"Score: {score}/10\n"
        digest += f"Title: {title}\n"
        digest += f"Speaker: {speaker if speaker else 'N/A'}\n"
        digest += f"Institution: {inst if inst else 'N/A'}\n"
        digest += f"Date: {date if date else 'TBD'}\n"
        digest += f"URL: {url}\n"
        digest += "------------------------------\n"
    
    return digest

def send_notifications():
    digest = generate_digest()
    if not digest:
        return

    print(f"Sending email digest via gmcli to {GMAIL_USER}...")
    
    try:
        # Use gmcli to send the email. 
        # The body is passed as a string.
        subprocess.run([
            "gmcli", GMAIL_USER, "send", 
            "--to", GMAIL_USER, 
            "--subject", "🚀 AI Events Intelligence Digest", 
            "--body", digest
        ], check=True)
        
        # Mark as notified in DB
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE events 
                SET status = 'notified' 
                WHERE score >= 7 AND status = 'discovered'
            ''')
            
            # Log notifications
            cursor.execute("SELECT id FROM events WHERE score >= 7 AND status = 'notified'")
            events_to_log = cursor.fetchall()
            for (eid,) in events_to_log:
                cursor.execute("INSERT INTO notifications (event_id) VALUES (?)", (eid,) )
            
            conn.commit()
        print("Notifications sent and logged successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error sending email via gmcli: {e}")

if __name__ == "__main__":
    send_notifications()
