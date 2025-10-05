from app.config_manager import ConfigManager
from app.data.program_data import add_category
from app.lang import Language

# -----------------------------
# Load config and language
# -----------------------------
config = ConfigManager()
lang_code = config.get("language", "en")  # default to 'en' if not set
lang = Language(lang_code)


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


# -----------------------------
# Example: access config in functions
# -----------------------------
def show_program_db_path():
    """
    Just an example function showing how to access the program DB path from config.
    """
    db_path = config.get("paths.program_db")
    print(f"Program database path: {db_path}")

