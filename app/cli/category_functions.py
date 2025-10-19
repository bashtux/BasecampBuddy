import sqlite3
from pathlib import Path
from app.config_manager import ConfigManager
from app.data.program_db import add_category
from app.lang import lang

# -----------------------------
# Load config and language
# -----------------------------
config = ConfigManager()


# -----------------------------
# category
# -----------------------------
def input_category():
    """
    Ask the user for a new category and insert it into the program DB.
    """
    print(lang.t("category_functions.title.new_category"))
    category_name = input(f"{lang.t('category_functions.cli.category_name')}: ").strip()
    description = input(f"{lang.t('category_functions.cli.category_description')}: ").strip()

    if category_name:
        add_category(category_name, description)
        print(lang.t('category_functions.msg.category_added').format(category_name=category_name))
    else:
        print(lang.t('category_functions.error.invalid_choice'))

def list_categories():
    """Print all available categories with description."""
    config = ConfigManager()
    db_path = Path(config.get("paths.program_db", "app/data/program_db.sqlite"))

    if not db_path.exists():
        print(lang.t("category_functions.error.no_program_db"))
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id_category, category, description FROM category ORDER BY category;")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print(lang.t("category_functions.error.no_category"))
        return

    print(lang.t("category_functions.title.list_caegories"))
    for row in rows:
        print(f"{row[0]}: {row[1]} — {row[2]}")
    print(lang.t("category_functions.cli.spacer"))


