import sqlite3
from pathlib import Path

from app.config_manager import ConfigManager  # assuming you have this
from app.lang import lang

# Load config once
config = ConfigManager()  # reads defaults + user config

# Determine project root
BASE_DIR = Path(__file__).resolve().parents[3]  # goes from app/data -> project root

# Path to program DB from config, fallback to default
program_db_rel = config.get("paths.user_db", "app/data/user_db.sqlite")
DB_PATH = (BASE_DIR / program_db_rel).resolve()

# Ensure parent folder exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


###############################################################################
#               Comment functions
###############################################################################

def add_comment(comment: str, parent_id: int, date: int, db_path: str = DB_PATH):
    """ Add a comment ot the user_db """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Comments (parent_id, date, comment) VALUES (?, ?, ?)", (parent_id, date, comment))
    conn.commit()
    conn.close()


#def update_comment(category_id: int, new_name: str, new_description: str):
#    """Update category name and description by ID."""
#    conn = sqlite3.connect(DB_PATH)
#    cursor = conn.cursor()
#    cursor.execute("""
#        UPDATE category
#        SET category = ?, description = ?
#        WHERE id_category = ?
#    """, (new_name, new_description, category_id))
#    conn.commit()
#    conn.close()


def get_comments_by_parent_id(parent_id: int):
    """Return a list of all comments with certain parent_id"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Comments WHERE parent_id = ? ORDER BY date", (parent_id,))
    results = cursor.fetchall()
    conn.close()
    return results


def get_comment_by_id(comment_id: int):
    """Return a single comment by ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Comments WHERE id_comment = ? SORT BY date", (comment_id,))
    result = cursor.fetchone()
    conn.close()
    return result


def delete_comments_by_parent_id(parent_id: int):
    """Delete all comments for a given parent."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM Comments WHERE parent_id = ?", (parent_id,))
    conn.commit()
    conn.close()
