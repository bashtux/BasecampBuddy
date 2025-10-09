import sqlite3
from pathlib import Path
from app.config_manager import ConfigManager
from app.data.program_db import add_category
from app.lang import get_lang

# -----------------------------
# Load config and language
# -----------------------------
config = ConfigManager()
lang = get_lang()


# -----------------------------
# CLI input helpers
# -----------------------------
def input_category():
    """
    Ask the user for a new category and insert it into the program DB.
    """
    print("\n=== Add New Category ===")
    category_name = input(f"{lang.t('program_db.category_name')}: ").strip()
    description = input(f"{lang.t('program_db.category_description')}: ").strip()

    if category_name:
        add_category(category_name, description)
        print(lang.t('program_db.category_added').format(category_name=category_name))
    else:
        print(lang.t('msg.invalid_choice'))

def list_categories():
    """Print all available categories with description."""
    config = ConfigManager()
    db_path = Path(config.get("paths.program_db", "app/data/program_db.sqlite"))

    if not db_path.exists():
        print("Program database not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id_category, category, description FROM category ORDER BY category;")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No categories found.")
        return

    print("\n=== Available Categories ===")
    for row in rows:
        print(f"{row[0]}: {row[1]} — {row[2]}")
    print("============================\n")


# -----------------------------
# Example: access config in functions
# -----------------------------
def show_program_db_path():
    """
    Just an example function showing how to access the program DB path from config.
    """
    db_path = config.get("paths.program_db")
    print(f"Program database path: {db_path}")

