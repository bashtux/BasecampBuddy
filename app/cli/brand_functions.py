import sqlite3
from pathlib import Path
from app.config_manager import ConfigManager
from app.core.utils.validation import prompt_validated_input, is_valid_url
from app.data.program_db import add_brand, get_all_brands
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
        prompt_key="brand.prompt.url",
        validator=is_valid_url,
        allow_empty=True,
        error_key="msg.invalid_url"
    )

    if brand_name:
        add_brand(brand_name, description, url)
        print(lang.t("brand_functions.msg.brand_added").format(brand_name=brand_name))
    else:
        print(lang.t("brand_category.error.no_name"))


def list_brands():
    """
    Print all available brands with description and URL
    """

    brands = get_all_brands()

    print(lang.t("brand_functions.title.list_brands"))
    for brand in brands:
        print(f"{brand[0]:<3} | {brand[1]} - {brand[3]}")

