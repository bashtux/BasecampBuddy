import sqlite3
from pathlib import Path

from app.config_manager import ConfigManager
from app.lang import lang

# Load config
config = ConfigManager()

# Get path to user DB, default fallback
user_db_path = config.get("paths.user_db", "app/data/user_db.sqlite")
DB_PATH = Path(user_db_path)

# Ensure parent folder exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Create empty SQLite file if it doesn't exist
if not DB_PATH.exists():
    # Connecting to SQLite will create the file automatically
    conn = sqilte3.connect(DB_PATH)
    conn.close()

def init_user_db(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Comments
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Comments (
            id_comment INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            item_type TEXT,
            date DATE NOT NULL,
            comment TEXT
        )
    """)

    # Gear
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Gear (
            id_gear INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT,
            brand INTEGER,
            size TEXT,
            mass_pcs INTEGER,
            price REAL,
            amount INTEGER,
            color TEXT,
            category INTEGER,
            description TEXT,
            prod_date DATE,
            checked BOOLEAN DEFAULT 0,
            last_checked DATE,
            lifespan INTEGER,
            kit_only BOOLEAN DEFAULT 0
        )
    """)

    # Kit
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Kit (
            id_kit INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            mass_correction INTEGER DEFAULT 0
        )
    """)

    # Kit-Gear mapping
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Kit_Gear (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kit_id INTEGER NOT NULL,
            gear_id INTEGER NOT NULL,
            amount INTEGER DEFAULT 1
        )
    """)

    # Trip
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Trip (
            id_trip INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            trip_month DATE,
            duration INTEGER,
            max_altitude INTEGER,
            no_people INTEGER,
            gear_mass_correction INTEGER DEFAULT 0,
            consumable_mass_correction INTEGER DEFAULT 0
        )
    """)

    # Trip items mapping
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Trip_Items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER NOT NULL,
            item_type TEXT NOT NULL,  -- 'gear' or 'kit'
            item_id INTEGER NOT NULL,
            amount INTEGER DEFAULT 1
        )
    """)

    # Trip consumables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Trip_Consumables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER NOT NULL,
            consumable_id INTEGER NOT NULL,
            amount INTEGER DEFAULT 1
        )
    """)

    conn.commit()
    conn.close()
    print(lang.t("user_db.msg.db_initialized", db_path=db_path))

