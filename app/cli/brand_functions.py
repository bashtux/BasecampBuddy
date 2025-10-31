import sqlite3
from pathlib import Path
from app.config_manager import ConfigManager
from app.core.utils.validation import prompt_validated_input, is_valid_url
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


def list_brands(brands: list, cols: list):
    """
    Print entries of brands only showing the defined entries of cols.
    """

    if isinstance(brands, list):
        if all(isinstance(brand, dict) for brand in brands):
            for info in brands:
                for i in cols:
                    print(info[i], end=" | ")
                print()
        else:
            for brand in brands:
                for i in cols:
                    print(brand[i], end=" | ")
                print()
    else:
        print(lang.t("brand_functions.error.not_list"))


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
