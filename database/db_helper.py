import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta

DB_PATH = 'events.db'

def init_db():
    """Initialize database with schema"""
    with sqlite3.connect(DB_PATH) as conn:
        with open('database/schema.sql', 'r') as f:
            conn.executescript(f.read())
    print("Database initialized successfully!")

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    try:
        yield conn
    finally:
        conn.close()

def insert_event(event_data):
    """Insert event into database, ignore duplicates"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        try:
            # Convert date/time objects to strings for SQLite
            event_date_str = str(event_data['event_date']) if event_data.get('event_date') else None
            event_time_str = str(event_data['event_time']) if event_data.get('event_time') else None
            
            cur.execute("""
                INSERT INTO events (title, event_date, event_time, location, url, 
                                  description, category, source, price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(title, event_date) DO UPDATE 
                SET updated_at = CURRENT_TIMESTAMP
            """, (
                event_data['title'],
                event_date_str,
                event_time_str,
                event_data['location'],
                event_data['url'],
                event_data['description'],
                event_data['category'],
                event_data['source'],
                event_data['price']
            ))
            conn.commit()
            return cur.lastrowid
        except Exception as e:
            conn.rollback()
            # Only print error if it's not a duplicate URL (which is expected)
            if 'UNIQUE constraint failed: events.url' not in str(e):
                print(f"Error inserting event: {e}")
            return None

def get_all_events():
    """Retrieve all events ordered by date and category"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM events 
            WHERE event_date >= date('now')
            ORDER BY category, event_date, event_time
        """)
        return [dict(row) for row in cur.fetchall()]

def clear_old_events():
    """Remove events older than 30 days"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            DELETE FROM events 
            WHERE event_date < date('now', '-30 days')
        """)
        deleted = cur.rowcount
        conn.commit()
        print(f"Deleted {deleted} old events")