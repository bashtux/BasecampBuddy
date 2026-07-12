import sqlite3
from pathlib import Path

from app.config_manager import ConfigManager
from app.lang import lang
from app.data import db
from app.cli.cli_utils import paged_list

config = ConfigManager()

CATEGORY_LIST_COLUMNS = {
    "id_category": "category_functions.fields.id",
    "name":        "category_functions.fields.name",
    "description": "category_functions.fields.description",
}


CATEGORY_TUPLE_KEYS = ["id_category", "name", "description"]

def _categories_to_dicts(categories: list) -> list[dict]:
    """Normalise tuples or dicts to dicts."""
    if not categories:
        return []
    if isinstance(categories[0], dict):
        return categories
    return [dict(zip(CATEGORY_TUPLE_KEYS, c)) for c in categories]


def input_category():
    """Ask the user for a new category and insert it into the program DB."""
    print(lang.t("category_functions.title.new_category"))
    category_name = input(f"{lang.t('category_functions.cli.category_name')}: ").strip()
    description   = input(f"{lang.t('category_functions.cli.category_description')}: ").strip()

    if category_name:
        db.add_category(category_name, description)
        print(lang.t('category_functions.msg.category_added').format(category_name=category_name))
    else:
        print(lang.t('category_functions.error.invalid_choice'))


def list_categories(default_cols: list[str] | None = None):
    """Paged list of all categories."""
    categories = db.get_all_categories()
    cat_dicts  = _categories_to_dicts(categories)

    def on_select(item):
        print(f"\n  {lang.t('category_functions.fields.id')}: {item.get('id_category')}")
        print(f"  {lang.t('category_functions.fields.name')}: {item.get('name')}")
        print(f"  {lang.t('category_functions.fields.description')}: {item.get('description') or '—'}")
        input(lang.t("category_functions.msg.enter_to_return"))

    paged_list(
        items        = cat_dicts,
        columns      = CATEGORY_LIST_COLUMNS,
        default_cols = ["name", "description"],
        on_select    = on_select,
        title_key    = "category_functions.title.list_categories",
        empty_key    = "category_functions.error.no_category",
    )


def pick_category() -> int | None:
    """Display categories and return the selected id_category, or None."""
    categories = db.get_all_categories()
    cat_dicts  = _categories_to_dicts(categories)

    if not cat_dicts:
        print(lang.t("category_functions.error.no_category"))
        return None

    print(lang.t("category_functions.title.list_categories"))
    col_w = 20
    print(f"  {'#':<4}{'ID':<6}{'Name':<{col_w}}")
    print("  " + "-" * (4 + 6 + col_w))
    for i, cat in enumerate(cat_dicts, 1):
        print(f"  {i:<4}{cat['id_category']:<6}{cat['name']:<{col_w}}")

    raw = input(lang.t("category_functions.cli.select_id")).strip()
    if not raw.isdigit() or not (0 <= int(raw) - 1 < len(cat_dicts)):
        print(lang.t("category_functions.error.invalid_choice"))
        return None

    return cat_dicts[int(raw) - 1]["id_category"]


def edit_category():
    """Allow user to edit a category (name and description)."""
    print(lang.t("category_functions.title.edit_category"))
    list_categories()

    try:
        category_id = int(input(lang.t("category_functions.cli.select_id")))
    except ValueError:
        print(lang.t("category_functions.error.invalid_choice"))
        return

    category = db.get_category_by_id(category_id)
    if not category:
        print(lang.t("category_functions.error.not_found"))
        return

    print(lang.t("category_functions.msg.current_values").format(name=category[1], desc=category[2]))

    new_name        = input(f"{lang.t('category_functions.cli.new_name')} ({category[1]}): ") or category[1]
    new_description = input(f"{lang.t('category_functions.cli.new_desc')} ({category[2]}): ") or category[2]

    db.update_category(category_id, new_name, new_description)
    print(lang.t("category_functions.msg.success"))


def delete_category():
    print(lang.t("delete_functions.title.delete_category"))
    row = _list_pick(
        db.get_all_categories(),
        ["id_category", "category", "description"],
        ["ID", "Name", "Description"],
    )
    if not row:
        return

    if not confirm("delete_functions.msg.confirm", name=row["name"]):
        print(lang.t("delete_functions.msg.cancelled"))
        return

    success = db.delete_category(row["id_category"])
    if success:
        print(lang.t("delete_functions.msg.deleted", name=row["category"]))
    else:
        print(lang.t("delete_functions.msg.has_references", name=row["category"]))
