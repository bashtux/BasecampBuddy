import sqlite3
from pathlib import Path

from app.config_manager import ConfigManager
from app.lang import lang

# Load config
config = ConfigManager()

# Determine project root
BASE_DIR = Path(__file__).resolve().parents[2]

# Path to program DB from config, fallback to default
user_db_rel = config.get("paths.user_db", "app/data/user_db.sqlite")
DB_PATH = (BASE_DIR / user_db_rel).resolve()

# Ensure parent folder exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    """
    Check if a table exists in the database.
    Returns True if the table exists, False otherwise.
    """
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,)
    )
    return cursor.fetchone() is not None


def init_user_db(db_path: Path | str = DB_PATH):
    """
    Initialize the user database with all necessary tables.
    Tables:
    - Gear
    - Kit
    - Trip
    - Comments
    Only creates tables if they do not exist already.
    """
    conn = sqlite3.connect(db_path)
    tables_created = False

    # Create Gear table if missing
    if not table_exists(conn, "Gear"):
        conn.execute("""
            CREATE TABLE Gear (
                id_gear INTEGER PRIMARY KEY,      -- unique identifier for gear
                name TEXT,                         -- gear name
                type TEXT,                         -- gear type/category
                brand INTEGER,                     -- foreign key to Brand
                size TEXT,                          -- gear size
                mass_pcs INTEGER,                  -- mass per piece
                price REAL,                        -- price per piece
                amount INTEGER,                     -- number of items
                color TEXT,                         -- color in HEX
                category INTEGER,                   -- foreign key to Category
                comments TEXT,                      -- list of comment IDs
                description TEXT,                   -- description of the gear
                prod_date TEXT,                     -- production/manufacture date
                checked INTEGER,                    -- boolean flag (0/1) if checked
                last_checked TEXT,                  -- last checked date
                lifespan INTEGER,                   -- lifespan in years (0 or NULL = infinite)
                kit_only INTEGER                     -- boolean (0/1) if only in kits
            )
        """)
        tables_created = True

    # Create Kit table if missing
    if not table_exists(conn, "Kit"):
        conn.execute("""
            CREATE TABLE Kit (
                id_kit INTEGER PRIMARY KEY,         -- unique identifier for kit
                name TEXT,                          -- kit name
                description TEXT,                   -- description of the kit
                comments TEXT,                      -- list of comment IDs
                gear_list TEXT,                     -- list of gear IDs
                mass_correction INTEGER,            -- manual mass correction
                gear_amount TEXT                    -- list of amounts for each gear
            )
        """)
        tables_created = True

    # Create Trip table if missing
    if not table_exists(conn, "Trip"):
        conn.execute("""
            CREATE TABLE Trip (
                id_trip INTEGER PRIMARY KEY,        -- unique identifier for trip
                name TEXT,                          -- trip name
                description TEXT,                   -- description of the trip
                comment TEXT,                       -- list of comment IDs
                tag TEXT,                           -- list of tags
                trip_month TEXT,                     -- trip month (YYYY-MM)
                duration INTEGER,                   -- duration in days
                max_altitude INTEGER,               -- max altitude in meters
                no_people INTEGER,                  -- number of participants
                gear TEXT,                          -- list of gear/kit IDs
                gear_amount TEXT,                   -- amounts for each gear/kit
                gear_mass_correction INTEGER,       -- manual gear mass correction
                consumables TEXT,                   -- list of consumable IDs
                consumable_amount TEXT,             -- amounts for consumables
                consumable_mass_correction INTEGER  -- manual consumable mass correction
            )
        """)
        tables_created = True

    # Create Comments table if missing
    if not table_exists(conn, "Comments"):
        conn.execute("""
            CREATE TABLE Comments (
                id_comment INTEGER PRIMARY KEY,     -- unique identifier for comment
                parent_id INTEGER,                  -- ID of gear/kit/trip this comment belongs to
                date TEXT,                          -- date of the comment
                comment TEXT                        -- comment text
            )
        """)
        tables_created = True

    conn.commit()
    conn.close()

    if tables_created:
        print(lang.t("user_db.msg.db_initialized", db_path=db_path))

def check_initialized(db_path: Path = DB_PATH) -> bool:
    """
    Returns True if all required tables exist in the user DB.
    """
    required_tables = ["Gear", "Kit", "Trip", "Comments"]
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = [row[0] for row in c.fetchall()]

    conn.close()
    return all(table in existing_tables for table in required_tables)
