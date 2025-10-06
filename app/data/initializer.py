from pathlib import Path
import sqlite3

from app.config_manager import ConfigManager
from app.data import program_data, user_db  # import your init functions here
from app.lang import get_lang

# Initialize selected language
lang = get_lang()

# Example: list of tables in each DB
PROGRAM_TABLES = ["brand", "category", "consumables"]
USER_TABLES = ["gear", "kit", "trip", "comments"]

def tables_exist(db_path: Path, required_tables: list[str]) -> bool:
    """Check if all required tables exist in the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    existing_tables = {row[0] for row in cursor.fetchall()}
    conn.close()
    return all(table in existing_tables for table in required_tables)

def ensure_program_db_initialized():
    db_path = Path(ConfigManager().get("paths.program_db", "app/data/program_db.sqlite"))
    db_path.parent.mkdir(parents=True, exist_ok=True)

    if not db_path.exists():
        # Just create the file if missing
        conn = sqlite3.connect(db_path)
        conn.close()

    if not tables_exist(db_path, PROGRAM_TABLES):
<<<<<<< HEAD
        print(lang.t("initialize_db.program_db_missing"))
=======
        print("Program DB tables missing. Initializing program DB...")
>>>>>>> 711de1e3f5174fdabe25dcb5f07c2e694c99f79b
        program_data.init_program_db(db_path)

def ensure_user_db_initialized():
    db_path = Path(ConfigManager().get("paths.user_db", "app/data/user_db.sqlite"))
    db_path.parent.mkdir(parents=True, exist_ok=True)

    if not db_path.exists():
        conn = sqlite3.connect(db_path)
        conn.close()

    if not tables_exist(db_path, USER_TABLES):
<<<<<<< HEAD
        print(lang.t("initialize_db.user_db_missing"))
=======
        print("User DB tables missing. Initializing user DB...")
>>>>>>> 711de1e3f5174fdabe25dcb5f07c2e694c99f79b
        user_db.init_user_db(db_path)

def initialize_all():
    """Call this at program startup to ensure all DBs are ready."""
    ensure_program_db_initialized()
    ensure_user_db_initialized()

