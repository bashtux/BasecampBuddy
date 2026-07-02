import sqlite3
from pathlib import Path
from app.config_manager import ConfigManager
from app.core.utils.validation import prompt_validated_input, is_valid_url
from app.cli.cli_utils import paged_list, print_table
from app.data import db
from app.lang import lang

#--------------------------
# Load config and language
#--------------------------
config = ConfigManager()

def input_brand():
    """
    Aks the user for a new brand and insert it into program DB:
    """

    print(lang.t("brand_functions.title.new_brand"))
    brand_name = input(f"{lang.t('brand_functions.cli.brand_name')}").strip()
    description = input(f"{lang.t('brand_functions.cli.description')}").strip()
    url = prompt_validated_input(
        prompt_key="brand_functions.cli.url",
        validator=is_valid_url,
        allow_empty=True,
        error_key="brand_functions.error.invalid_url"
    )

    if brand_name:
        db.add_brand(brand_name, description, url)
        print(lang.t("brand_functions.msg.brand_added").format(brand_name=brand_name))
    else:
        print(lang.t("brand_functions.error.no_name"))


BRAND_LIST_COLUMNS = {
    "id_brand":    "brand_functions.fields.id",
    "name":        "brand_functions.fields.name",
    "description": "brand_functions.fields.description",
    "url":         "brand_functions.fields.url",
}

DEFAULT_BRAND_COLS = ["id_brand", "name", "url"]

# tuples from get_all_brands() -> dicts
BRAND_TUPLE_KEYS = ["id_brand", "name", "description", "url"]

def _brands_to_dicts(brands: list) -> list[dict]:
    """Normalise tuples or dicts to dicts."""
    if not brands:
        return []
    if isinstance(brands[0], dict):
        return brands
    return [dict(zip(BRAND_TUPLE_KEYS, b)) for b in brands]


def list_brands(brands: list | None = None, cols: list | None = None):
    """
    Display brands using paged_list.
    - brands: optional pre-fetched list (tuples or dicts); fetches all if None
    - cols:   optional list of field keys to show (overrides default)
    """
    if brands is None:
        brands = db.get_all_brands()

    brand_dicts = _brands_to_dicts(brands)

    # If specific cols were passed (e.g. from gear search), use print_table
    # for a quick non-paged inline display
    if cols is not None:
        col_keys = [c if isinstance(c, str) else BRAND_TUPLE_KEYS[c] for c in cols]
        labels   = [lang.t(BRAND_LIST_COLUMNS.get(k, k)) for k in col_keys]
        print_table(brand_dicts, col_keys, labels)
        return

    # Full paged list
    def on_select(item):
        print(f"\n  {lang.t('brand_functions.fields.id')}: {item.get('id_brand')}")
        print(f"  {lang.t('brand_functions.fields.name')}: {item.get('name')}")
        print(f"  {lang.t('brand_functions.fields.description')}: {item.get('description') or '—'}")
        print(f"  {lang.t('brand_functions.fields.url')}: {item.get('url') or '—'}")
        input(lang.t("brand_functions.msg.enter_to_return"))

    paged_list(
        items        = brand_dicts,
        columns      = BRAND_LIST_COLUMNS,
        default_cols = DEFAULT_BRAND_COLS,
        on_select    = on_select,
        title_key    = "brand_functions.title.list_brands",
        empty_key    = "brand_functions.error.not_found",
    )

def edit_brand():
    """Allow user to edit a brand (name, description and URL)."""
    print(lang.t("brand_functions.title.edit_brand"))
    list_brands()

    try:
        brand_id = int(input(lang.t("brand_functions.cli.select_id")))
    except ValueError:
        print(lang.t("brand_functions.error.invalid_choice"))
        return

    brand = db.get_brand_by_id(brand_id)
    if not brand:
        print(lang.t("brand_functions.error.not_found"))
        return

    print(lang.t("brand_functions.msg.current_values").format(name=brand[1], desc=brand[2], url=brand[3]))

    new_name = input(f"({brand[1]})\n {lang.t('brand_functions.cli.new_name')}: ") or brand[1]
    new_description = input(f"({brand[2]})\n {lang.t('brand_functions.cli.new_description')}: ") or brand[2]
    print("("+brand[3]+")")
    new_url = (
        prompt_validated_input(
            prompt_key="brand_functions.cli.new_url",
            validator=is_valid_url,
            allow_empty=True,
            error_key="brand_functions.error.invalid_url"
        )
    or brand[3] 
    )

    db.update_brand(brand_id, new_name, new_description, new_url)
    print(lang.t("brand_functions.msg.success"))
    return
