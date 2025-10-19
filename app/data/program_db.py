import sqlite3
from pathlib import Path

from app.config_manager import ConfigManager  # assuming you have this
from app.lang import lang

# Load config once
config = ConfigManager()  # reads defaults + user config

# Get path to program DB, default fallback
program_db_path = config.get("paths.program_db", "app/data/program_db.sqlite")
DB_PATH = Path(program_db_path)

# Ensure parent folder exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Create empty SQLite file if it doesn't exist
if not DB_PATH.exists():
    # Connecting to SQLite will create the file automatically
    conn = sqlite3.connect(DB_PATH)
    conn.close()

def init_program_db(db_path: str | Path = DB_PATH):
    """
    Initialize the program database with the reference tables:
    - Brand
    - Category
    - Consumables
    """

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)  # ensure folder exists

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # -----------------------------
    # Brand table
    # -----------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Brand (
            id_brand INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT
        )
    """)

    # -----------------------------
    # Category table
    # -----------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Category (
            id_category INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            description TEXT
        )
    """)

    # -----------------------------
    # Consumables table
    # -----------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Consumables (
            id_consumable INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            weight INTEGER
        )
    """)

    conn.commit()
    conn.close()
    print(lang.t("program_db.msg.db_initialized", db_path=db_path))


# Optional: helper function to insert sample data
def add_brand(name: str, url: str = "", db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Brand (name, url) VALUES (?, ?)", (name, url))
    conn.commit()
    conn.close()


def add_category(category: str, description: str = "", db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Category (category, description) VALUES (?, ?)", (category, description))
    conn.commit()
    conn.close()


def add_consumable(name: str, description: str = "", weight: int = 0, db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Consumables (name, description, weight) VALUES (?, ?, ?)",
        (name, description, weight)
    )
    conn.commit()
    conn.close()

