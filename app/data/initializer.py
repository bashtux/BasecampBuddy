from pathlib import Path
import sqlite3

from app.config_manager import ConfigManager
from app.data import program_db, user_db  # import your init functions here
from app.lang import lang

# load config
config = ConfigManager()

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
        print(lang.t("initializer.error.no_program_db"))
        program_db.init_program_db(db_path)

def ensure_user_db_initialized():
    db_path = Path(ConfigManager().get("paths.user_db", "app/data/user_db.sqlite"))
    db_path.parent.mkdir(parents=True, exist_ok=True)

    if not db_path.exists():
        conn = sqlite3.connect(db_path)
        conn.close()

    if not tables_exist(db_path, USER_TABLES):
        print(lang.t("initializer.error.no_user_db"))
        user_db.init_user_db(db_path)

def initialize_all():
    """Call this at program startup to ensure all DBs are ready."""
    ensure_program_db_initialized()
    ensure_user_db_initialized()

