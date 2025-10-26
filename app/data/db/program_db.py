import sqlite3
from pathlib import Path

from app.config_manager import ConfigManager  # assuming you have this
from app.lang import lang

# Load config once
config = ConfigManager()  # reads defaults + user config

# Determine project root
BASE_DIR = Path(__file__).resolve().parents[3]  # goes from app/data -> project root

# Path to program DB from config, fallback to default
program_db_rel = config.get("paths.program_db", "app/data/program_db.sqlite")
DB_PATH = (BASE_DIR / program_db_rel).resolve()

# Ensure parent folder exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


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
        UPDATE Brand
        SET name = ?, description = ?, url = ?
        WHERE id_brand = ?
    """, (new_name, new_description, new_url, brand_id))
    conn.commit()
    conn.close()


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

###############################################################################
#               Consumables functions
###############################################################################

def add_consumable(name: str, description: str = "", weight: int = 0, db_path: str = DB_PATH):
    """Add new consumable to database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Consumable (name, description, weight) VALUES (?, ?, ?)", (name, description, weight))
    conn.commit()
    conn.close()


def update_consumable(consumable_id: int, new_name: str, new_description: str, new_weight: str):
    """Update consumable name, description and weightL by ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Consumable
        SET name = ?, description = ?, weight = ?
        WHERE id_consumable = ?
    """, (new_name, new_description, new_weight, consumable_id))
    conn.commit()
    conn.close()


def get_all_consumables():
    """ Return a list of all consumables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id_consumable, name, description, weight FROM Consumable ORDER BY name")
    results = cursor.fetchall()
    conn.close()
    return results


def get_consumable_by_id(consumable_id: int):
    """Return a single consumable by ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id_consumable, name, description, weight FROM Consumable WHERE id_consumable = ?", (consumable_id,))
    result = cursor.fetchone()
    conn.close()
    return result

