import sqlite3
from pathlib import Path
from app.config_manager import ConfigManager
from app.data.program_db import add_category, get_category_by_id, update_category, get_all_categories
from app.lang import lang

# -----------------------------
# Load config and language
# -----------------------------
config = ConfigManager()


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
    categories = get_all_categories()
    if not categories:
        print(lang.t("category_functions.error.no_category"))
        return

    print(lang.t("category_functions.title.list_categories"))
    for cat in categories:
        print(f"{cat[0]:<3} | {cat[1]} — {cat[2]}")


def edit_category():
    """Allow user to edit a category (name and description)."""
    print(lang.t("category_functions.title.edit_category"))
    list_categories()  # Reuse your existing function

    try:
        category_id = int(input(lang.t("category_functions.cli.select_id")))
    except ValueError:
        print(lang.t("category_functions.error.invalid_choice"))
        return

    category = get_category_by_id(category_id)
    if not category:
        print(lang.t("category_functions.error.not_found"))
        return

    print(lang.t("category_functions.msg.current_values").format(name=category[1], desc=category[2]))

    new_name = input(f"{lang.t('category_functions.cli.new_name')} ({category[1]}): ") or category[1]
    new_description = input(f"{lang.t('category_functions.cli.new_desc')} ({category[2]}): ") or category[2]

    update_category(category_id, new_name, new_description)
    print(lang.t("category_functions.msg.success"))
