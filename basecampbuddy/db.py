import sqlite3
from sqlite3 import Connection
from pathlib import Path

DB_FILE = Path(__file__).parent / "basecampbuddy.db"

def get_connection() -> Connection:
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # allows dict-like access
    return conn

def initialize_db():
    """Create tables if they don’t exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gear_item (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        purchase_date TEXT NOT NULL,
        lifespan_years INTEGER NOT NULL,
        last_check TEXT
    )
    """)

    conn.commit()
    conn.close()

