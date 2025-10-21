# app/data/initializer.py
from pathlib import Path
from app.data import program_db, user_db
from app.config_manager import ConfigManager
from app.lang import lang

# Load configuration
config = ConfigManager()
program_db_path: Path = Path(config.get("paths.program_db", "app/data/program_db.sqlite"))
user_db_path: Path = Path(config.get("paths.user_db", "app/data/user_db.sqlite"))

# Ensure parent folders exist
program_db_path.parent.mkdir(parents=True, exist_ok=True)
user_db_path.parent.mkdir(parents=True, exist_ok=True)

def ensure_program_db_initialized():
    """Initialize the program database if required."""
    if not program_db_path.exists() or not program_db.check_initialized(program_db_path):
        program_db.init_program_db(program_db_path)
        print(lang.t("initializer.msg.program_db_created").format(db_path=program_db_path))
    else:
        # Optional: only debug info, not standard user message
        print(lang.t("initializer.msg.program_db_found").format(db_path=program_db_path))

def ensure_user_db_initialized():
    """Initialize the user database if required."""
    if not user_db_path.exists() or not user_db.check_initialized(user_db_path):
        user_db.init_user_db(user_db_path)
        print(lang.t("initializer.msg.user_db_created").format(db_path=user_db_path))
    else:
        # Optional: only debug info
        print(lang.t("initializer.msg.user_db_found").format(db_path=user_db_path))

def initialize_all():
    """
    Initialize both program and user databases.
    Call this at the very start of the application.
    """
    ensure_program_db_initialized()
    ensure_user_db_initialized()
    print(lang.t("initializer.msg.db_ready"))

