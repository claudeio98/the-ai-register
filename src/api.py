from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import sqlite3
from datetime import datetime
from db import get_connection

app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    show_past: bool = False
):
    # Base query
    query = "SELECT id, title, speaker, institution, date, url, score, status FROM events"
    params = []
    conditions = []

    if status:
        conditions.append("status = ?")
        params.append(status)

    # Date filtering
    now = datetime.now().strftime("%Y-%m-%d")
    if not show_past:
        conditions.append("date >= ?")
        params.append(now)
    else:
        conditions.append("date < ?")
        params.append(now)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    # Ordering
    # Only allow specific columns for sorting to prevent SQL injection
    allowed_sort_cols = {"date": "date", "score": "score", "title": "title"}
    sort_col = allowed_sort_cols.get(sort_by, "date")
    sort_dir = "ASC" if order.lower() == "asc" else "DESC"
    
    query += f" ORDER BY {sort_col} {sort_dir}"

    rows = query_db(query, params)
    
    # Convert to list of dicts
    columns = [description[0] for description in get_connection().execute(query, params).description]
    return [dict(zip(columns, row)) for row in rows]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082)
