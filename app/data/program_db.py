import sqlite3
from pathlib import Path

from app.config_manager import ConfigManager  # assuming you have this
from app.lang import lang

# Load config once
config = ConfigManager()  # reads defaults + user config

# Determine project root
BASE_DIR = Path(__file__).resolve().parents[2]  # goes from app/data -> project root

# Path to program DB from config, fallback to default
program_db_rel = config.get("paths.program_db", "app/data/program_db.sqlite")
DB_PATH = (BASE_DIR / program_db_rel).resolve()

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


def init_program_db(db_path: Path | str = DB_PATH):
    """
    Initialize the program database with reference tables.
    Tables:
    - Brand
    - Category
    - Consumables
    Only creates tables if they do not exist already.
    """
    conn = sqlite3.connect(db_path)
    tables_created = False

    # Create Brand table if missing
    if not table_exists(conn, "Brand"):
        conn.execute("""
            CREATE TABLE Brand (
                id_brand INTEGER PRIMARY KEY,  -- unique identifier for brand
                name TEXT,                     -- brand name
                description TEXT,              -- brand description
                url TEXT                       -- brand website URL
            )
        """)
        tables_created = True

    # Create Category table if missing
    if not table_exists(conn, "Category"):
        conn.execute("""
            CREATE TABLE Category (
                id_category INTEGER PRIMARY KEY,  -- unique identifier for category
                category TEXT,                    -- category name
                description TEXT                  -- description of the category
            )
        """)
        tables_created = True

    # Create Consumables table if missing
    if not table_exists(conn, "Consumables"):
        conn.execute("""
            CREATE TABLE Consumables (
                id_consumable INTEGER PRIMARY KEY,  -- unique identifier for consumable
                name TEXT,                          -- consumable name
                description TEXT,                   -- description of consumable
                weight INTEGER                      -- weight in grams (or units)
            )
        """)
        tables_created = True

    conn.commit()
    conn.close()

    if tables_created:
        print(lang.t("program_db.msg.db_initialized", db_path=db_path))

###############################################################################
#               Category functions
###############################################################################

def add_category(category: str, description: str = "", db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Category (category, description) VALUES (?, ?)", (category, description))
    conn.commit()
    conn.close()


def update_category(category_id: int, new_name: str, new_description: str):
    """Update category name and description by ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE category
        SET category = ?, description = ?
        WHERE id_category = ?
    """, (new_name, new_description, category_id))
    conn.commit()
    conn.close()


def get_all_categories():
    """Return a list of all categories."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id_category, category, description FROM category ORDER BY category")
    results = cursor.fetchall()
    conn.close()
    return results


def get_category_by_id(category_id: int):
    """Return a single category by ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id_category, category, description FROM category WHERE id_category = ?", (category_id,))
    result = cursor.fetchone()
    conn.close()
    return result

###############################################################################
#               Brand functions
###############################################################################

def add_brand(name: str, description: str = "", url: str = "", db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Brand (name, description, url) VALUES (?, ?, ?)", (name, description, url))
    conn.commit()
    conn.close()


def update_brand(brand_id: int, new_name: str, new_description: str, new_url: str):
    """Update brand name, description and URL by ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE brand
        SET name = ?, description = ?, url = ?
        WHERE id_brand = ?
    """, (new_name, new_description, new_url, brand_id))
    conn.commit()


def get_all_brands():
    """ Return a list of all brands """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id_brand, name, description, url FROM brand ORDER BY name")
    results = cursor.fetchall()
    conn.close()
    return results


def get_brand_by_id(brand_id: int):
    """Return a single brand by ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id_brand, name, description, url FROM brand WHERE id_brand = ?", (brand_id,))
    result = cursor.fetchone()
    conn.close()
    return result


def check_initialized(db_path: Path = DB_PATH) -> bool:
    """
    Returns True if all required tables exist in the program DB.
    """
    required_tables = ["Brand", "Category", "Consumables"]
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = [row[0] for row in c.fetchall()]

    conn.close()
    return all(table in existing_tables for table in required_tables)
