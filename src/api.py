from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sqlite3
import re
from datetime import datetime
from db import get_connection
from dedup import get_duplicate_count
from feedback_notifier import notify_feedback

# Simple in-memory rate limiter for feedback endpoint
import time as _time
_feedback_rate_limit: dict[str, float] = {}
_FEEDBACK_RATE_LIMIT_SECONDS = 30


def _check_feedback_rate_limit(client_ip: str) -> None:
    """Raise HTTPException if the client has submitted feedback too recently."""
    now = _time.time()
    last = _feedback_rate_limit.get(client_ip)
    if last and (now - last) < _FEEDBACK_RATE_LIMIT_SECONDS:
        retry_after = int(_FEEDBACK_RATE_LIMIT_SECONDS - (now - last))
        raise HTTPException(
            status_code=429,
            detail=f"Please wait {retry_after} seconds before submitting again.",
        )
    _feedback_rate_limit[client_ip] = now

app = FastAPI(title="London AI Radar API")

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "London AI Radar API"}

def query_db(query, args=(), one=False):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, args)
    rv = cursor.fetchall()
    conn.close()
    return (rv[0] if one else rv)

@app.get("/events")
def get_events(
    status: Optional[str] = None,
    sort_by: str = "date",
    order: str = "asc",
    show_past: bool = False,
    subscriber_email: Optional[str] = None,
    include_source: bool = False
):
    # Base query — only canonical events (canonical_event_id IS NULL)
    # Include discovery_source_id for provenance tracking
    query = """SELECT e.id, e.title, e.speaker, e.institution, e.date, e.url, e.score,
                      e.status, e.discovery_source_id
               FROM events e
               WHERE e.canonical_event_id IS NULL"""
    params = []
    conditions = []

    if status:
        conditions.append("e.status = ?")
        params.append(status)

    # Date filtering
    now = datetime.now().strftime("%Y-%m-%d")
    if not show_past:
        conditions.append("e.date >= ?")
        params.append(now)
    else:
        conditions.append("e.date < ?")
        params.append(now)

    # Filter hidden events for subscribed users
    if subscriber_email:
        email = subscriber_email.strip().lower()
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM subscribers WHERE email = ? AND active = 1", (email,))
            if cursor.fetchone():
                conditions.append("e.id NOT IN (SELECT event_id FROM hidden_events WHERE subscriber_email = ?)")
                params.append(email)

    if conditions:
        query += " AND " + " AND ".join(conditions)

    # Ordering
    allowed_sort_cols = {"date": "e.date", "score": "e.score", "title": "e.title"}
    sort_col = allowed_sort_cols.get(sort_by, "e.date")
    sort_dir = "ASC" if order.lower() == "asc" else "DESC"

    query += f" ORDER BY {sort_col} {sort_dir}"

    rows = query_db(query, params)
    columns = [description[0] for description in get_connection().execute(query, params).description]
    events_list = [dict(zip(columns, row)) for row in rows]

    # Add duplicate count for each event
    conn = get_connection()
    cursor = conn.cursor()
    for e in events_list:
        e["duplicate_count"] = get_duplicate_count(cursor, e["id"])

        # If include_source is true, look up source details
        if include_source and e.get("discovery_source_id"):
            cursor.execute(
                "SELECT id, url, category FROM sources WHERE id = ?",
                (e["discovery_source_id"],)
            )
            source_row = cursor.fetchone()
            if source_row:
                e["source"] = {
                    "id": source_row[0],
                    "url": source_row[1],
                    "category": source_row[2]
                }
            else:
                e["source"] = None
        elif include_source:
            e["source"] = None

    # Batch query for other_sources: fetch duplicate URLs for events with duplicates
    # Uses a single grouped query to avoid N+1
    events_with_dups = [e for e in events_list if e["duplicate_count"] > 0]
    if events_with_dups:
        dup_ids = [e["id"] for e in events_with_dups]
        placeholders = ",".join("?" * len(dup_ids))
        cursor.execute(
            f"SELECT canonical_event_id, url, COALESCE(title, url) AS label "
            f"FROM events WHERE canonical_event_id IN ({placeholders}) "
            f"ORDER BY score DESC",
            dup_ids
        )
        other_rows = cursor.fetchall()
        # Group by canonical_event_id
        other_map = {}
        for ce_id, url, label in other_rows:
            other_map.setdefault(ce_id, []).append({"url": url, "title": label})
        for e in events_list:
            e["other_sources"] = other_map.get(e["id"], [])
    else:
        for e in events_list:
            e["other_sources"] = []

    conn.close()

    return events_list

class SubscribeRequest(BaseModel):
    email: str

class UnsubscribeRequest(BaseModel):
    email: str

class FeedbackRequest(BaseModel):
    category: str
    message: str

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

def is_valid_email(email: str) -> bool:
    return bool(re.match(EMAIL_REGEX, email.strip()))

@app.post("/subscribe")
def subscribe(req: SubscribeRequest):
    email = req.email.strip().lower()
    if not is_valid_email(email):
        return {"success": False, "error": "Invalid email format"}
    
    with get_connection() as conn:
        cursor = conn.cursor()
        # Check if email already exists
        cursor.execute("SELECT id, active FROM subscribers WHERE email = ?", (email,))
        existing = cursor.fetchone()
        
        if existing:
            if existing[1] == 0:
                # Reactivate
                cursor.execute("UPDATE subscribers SET active = 1, subscribed_at = CURRENT_TIMESTAMP WHERE email = ?", (email,))
                return {"success": True, "message": "Subscription reactivated!"}
            else:
                return {"success": True, "message": "Already subscribed!"}
        else:
            cursor.execute("INSERT INTO subscribers (email) VALUES (?)", (email,))
            return {"success": True, "message": "Subscribed successfully!"}

@app.post("/unsubscribe")
def unsubscribe(req: UnsubscribeRequest):
    email = req.email.strip().lower()
    if not is_valid_email(email):
        return {"success": False, "error": "Invalid email format"}
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM subscribers WHERE email = ?", (email,))
        existing = cursor.fetchone()
        
        if not existing:
            return {"success": False, "error": "Email not found in our subscribers list"}
        
        cursor.execute("UPDATE subscribers SET active = 0 WHERE email = ?", (email,))
        return {"success": True, "message": "Unsubscribed successfully!"}

@app.post("/events/{event_id}/hide")
def hide_event(event_id: int, subscriber_email: str = Query(...)):
    email = subscriber_email.strip().lower()
    if not is_valid_email(email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    with get_connection() as conn:
        cursor = conn.cursor()
        # Validate subscriber is active
        cursor.execute("SELECT id FROM subscribers WHERE email = ? AND active = 1", (email,))
        if not cursor.fetchone():
            raise HTTPException(status_code=403, detail="No active subscription found for this email")
        
        # Insert or ignore if already hidden
        cursor.execute(
            "INSERT OR IGNORE INTO hidden_events (event_id, subscriber_email) VALUES (?, ?)",
            (event_id, email)
        )
        already_hidden = cursor.rowcount == 0
        conn.commit()
    
    return {"success": True, "already_hidden": already_hidden}


@app.post("/events/{event_id}/unhide")
def unhide_event(event_id: int, subscriber_email: str = Query(...)):
    email = subscriber_email.strip().lower()
    if not is_valid_email(email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM hidden_events WHERE event_id = ? AND subscriber_email = ?",
            (event_id, email)
        )
        conn.commit()
    
    return {"success": True}


@app.post("/events/unhide-all")
def unhide_all_events(subscriber_email: str = Query(...)):
    email = subscriber_email.strip().lower()
    if not is_valid_email(email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM subscribers WHERE email = ? AND active = 1", (email,))
        if not cursor.fetchone():
            raise HTTPException(status_code=403, detail="No active subscription found for this email")
        
        cursor.execute("DELETE FROM hidden_events WHERE subscriber_email = ?", (email,))
        deleted = cursor.rowcount
        conn.commit()
    
    return {"success": True, "unhidden_count": deleted}


@app.get("/events/hidden")
def get_hidden_events(subscriber_email: str = Query(...)):
    email = subscriber_email.strip().lower()
    
    with get_connection() as conn:
        cursor = conn.cursor()
        # Validate subscriber
        cursor.execute("SELECT id FROM subscribers WHERE email = ? AND active = 1", (email,))
        if not cursor.fetchone():
            raise HTTPException(status_code=403, detail="No active subscription found for this email")
        
        # Fetch hidden events with event details
        cursor.execute('''
            SELECT e.id, e.title, e.date, e.score, e.institution
            FROM hidden_events h
            JOIN events e ON e.id = h.event_id
            WHERE h.subscriber_email = ?
            ORDER BY h.hidden_at DESC
        ''', (email,))
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
    
    return [dict(zip(columns, row)) for row in rows]


@app.get("/events/check-subscriber")
def check_subscriber(email: str = Query(...)):
    email = email.strip().lower()
    if not is_valid_email(email):
        return {"active": False, "email": email}
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, active FROM subscribers WHERE email = ?", (email,))
        row = cursor.fetchone()
    
    if row and row[1] == 1:
        return {"active": True, "email": email}
    return {"active": False, "email": email}


@app.post("/api/feedback")
def submit_feedback(req: FeedbackRequest, request: Request):
    category = req.category.strip()
    message = req.message.strip()
    
    allowed_categories = ["Bug Report", "Missing Talk/Event", "Feature Request", "General Feedback"]
    
    if not category or not message:
        raise HTTPException(status_code=400, detail="Category and message are required")
    
    if category not in allowed_categories:
        raise HTTPException(status_code=400, detail=f"Invalid category. Allowed: {', '.join(allowed_categories)}")
    
    # Enforce rate limit per client IP
    client_ip = request.client.host if request.client else "unknown"
    _check_feedback_rate_limit(client_ip)
    
    notify_feedback(category, message)
    
    return {"success": True, "message": "Thank you for your feedback!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082)
