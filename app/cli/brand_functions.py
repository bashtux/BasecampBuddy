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
    Ask the user for a new brand and insert it into program DB:
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
        # Clear cache so new brand is loaded next time
        Brand.clear_cache()
    else:
        print(lang.t("brand_functions.error.no_name"))

# column key --> translation key (resolved via lang.t() at display time
BRAND_LIST_COLUMNS = {
    "id_brand":    "brand.id_brand",
    "name":        "brand.name",
    "description": "brand.description",
    "url":         "brand.url",
}

def list_brands(all_brands: list | None = None, cols: list | None = None):
    """
    Display brands using paged_list.
    - all_brands: optional pre-fetched list of Brand objects; fetches all if None
    - cols:       optional list of field keys to show (overrides default)
    """
    if all_brands is None:
        all_brands = db.get_all_brands()  # Returns list of Brand objects
    
    # If specific cols were passed (e.g. from gear search), use print_table
    # for a quick non-paged inline display
    if cols is not None:
        col_keys = cols
        labels = [lang.t(BRAND_LIST_COLUMNS.get(k, k)) for k in col_keys]
        print_table(all_brands, col_keys, labels)
        return

    # Full paged list
    def on_select(brand: Brand):
        """Display full details for selected brand"""
        print(f"\n  {lang.t('brand.id_brand')}: {brand.id_brand}")
        print(f"  {lang.t('brand.name')}: {brand.name}")
        print(f"  {lang.t('brand.description')}: {brand.description or '—'}")
        print(f"  {lang.t('brand.url')}: {brand.url or '—'}")
        input(lang.t("brand_functions.msg.enter_to_return"))

    paged_list(
        items        = all_brands,
        columns      = BRAND_LIST_COLUMNS,
        default_cols = ["name", "url"],
        on_select    = on_select,
        title_key    = "brand_functions.title.list_brands",
        empty_key    = "brand_functions.error.not_found",
    )

def edit_brand():
    """Allow user to edit a brand (name, description and URL)."""
    print(lang.t("brand_functions.title.edit_brand"))
    
    # Get all brands
    all_brands = db.get_all_brands()
    
    # Show simple table for selection
    print_table(
        items   = all_brands,
        columns = ["id_brand", "name", "url"],
        labels  = ["ID", "Name", "Website"],
    )
    
    try:
        brand_id = int(input(lang.t("brand_functions.cli.select_id")))
    except ValueError:
        print(lang.t("brand_functions.error.invalid_choice"))
        return

    brand = db.get_brand_by_id(brand_id)
    if not brand:
        print(lang.t("brand_functions.error.not_found"))
        return

    print(lang.t("brand_functions.msg.current_values").format(
        name=brand.name, 
        desc=brand.description, 
        url=brand.url
    ))

    new_name = input(f"({brand.name})\n {lang.t('brand_functions.cli.new_name')}: ") or brand.name
    new_description = input(f"({brand.description or ''})\n {lang.t('brand_functions.cli.new_description')}: ") or brand.description
    
    print("(" + (brand.url or "") + ")")
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
    
    # Clear cache so updated brand is reloaded
    Brand.clear_cache()
    return
