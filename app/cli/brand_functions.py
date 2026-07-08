import sqlite3
from pathlib import Path
from app.config_manager import ConfigManager
from app.core.utils.validation import prompt_validated_input, is_valid_url
from app.core.brand import Brand
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

# column key --> translation key (resolved via lang.t() at display time
#BRAND_LIST_COLUMNS = {
#    "id_brand":    "brand_functions.fields.id",
#    "name":        "brand_functions.fields.name",
#    "description": "brand_functions.fields.description",
#    "url":         "brand_functions.fields.url",
#}
BRAND_LIST_COLUMNS = {
    "id_brand":    "brand.id_brand",
    "name":        "brand.name",
    "description": "brand.description",
    "url":         "brand.url",
}

def list_brands(all_brands: list | None = None, cols: list | None = None):
    """
    Display brands using paged_list.
    - brands: optional pre-fetched list (tuples or dicts); fetches all if None
    - cols:   optional list of field keys to show (overrides default)
    """
    if all_brands is None:
        all_brands = db.get_all_brands()
    
    brands = []

    for i in all_brands:
        row = {k: v for k, v in i.items() if k in {"id_brand", "name", "description", "url"}}
        brands.append(Brand(**row))

    # If specific cols were passed (e.g. from gear search), use print_table
    # for a quick non-paged inline display
    if cols is not None:
        col_keys = [c if isinstance(c, str) else BRAND_TUPLE_KEYS[c] for c in cols]
        labels   = [lang.t(BRAND_LIST_COLUMNS.get(k, k)) for k in col_keys]
        print_table(brands, col_keys, labels)
        return

    # Full paged list
    def on_select(item):
        print(f"\n  {lang.t('brand_functions.fields.id')}: {brand.id_brand}")
        print(f"  {lang.t('brand_functions.fields.name')}: {brand.name}")
        print(f"  {lang.t('brand_functions.fields.description')}: {brand.description or '—'}")
        print(f"  {lang.t('brand_functions.fields.url')}: {brand.url or '—'}")
        input(lang.t("brand_functions.msg.enter_to_return"))

    paged_list(
        items        = brand_dicts,
        columns      = BRAND_LIST_COLUMNS,
        default_cols = ["name", "url"],
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

    print(lang.t("brand_functions.msg.current_values").format(name=brand.name, desc=brand.description, url=brand.url))

    new_name = input(f"({brand[1]})\n {lang.t('brand_functions.cli.new_name')}: ") or brand.name
    new_description = input(f"({brand[2]})\n {lang.t('brand_functions.cli.new_description')}: ") or brand.description
    print("("+brand.url+")")
    new_url = (
        prompt_validated_input(
            prompt_key="brand_functions.cli.new_url",
            validator=is_valid_url,
            allow_empty=True,
            error_key="brand_functions.error.invalid_url"
        )
    or brand.url 
    )

    db.update_brand(brand_id, new_name, new_description, new_url)
    print(lang.t("brand_functions.msg.success"))
    return
