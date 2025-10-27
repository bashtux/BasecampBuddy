import sqlite3
from pathlib import Path

from app.config_manager import ConfigManager
from app.lang import lang
from app.data import db

from app.core.utils.validation import prompt_validated_input, is_positive_number
from app.core.gear_item import Gear

#------------------------------
# Load config and language
#------------------------------

def input_gear():
    """
    Ask the user for a new gear and insert into user_db
    """

    print(lang.t("gear_functions.title.new_gear"))
    name = input(f"{lang.t('gear_functions.cli.gear_name')}").strip()
    variant = input(f"{lang.t('gear_functions.cli.gear_variant')}").strip()
    brand = input(f"{lang.t('gear_functions.cli.gear_brand')}").strip()
    size = input(f"{lang.t('gear_functions.cli.gear_size')}").strip()
    mass_pcs = input(f"{lang.t('gear_functions.cli.gea_mass_pcs')}").strip()
    price = input(f"{lang.t('gear_functions.cli.gear_price')}").strip()
    amount = input(f"{lang.t('gear_functions.cli.gear_amount')}").strip()
    color = input(f"{lang.t('gear_functions.cli.gear_color')}").strip()
    category = input(f"{lang.t('gear_functions.cli.gear_category')}").strip()
    description = input(f"{lang.t('gear_functions.cli.gear_description')}").strip()
    prod_date = input(f"{lang.t('gear_functions.cli.gear_prod_date')}").strip()
    lifespan = input(f"{lang.t('gear_functions.cli.gear_lifespan')}").strip()
    kit_only = input(f"{lang.t('gear_functions.cli.gear_kit_only')}").strip()

#    url = prompt_validated_input(
#        prompt_key="brand_functions.cli.url",
#        validator=is_positive_number,
#        allow_empty=True,
#        error_key="brand_functions.error.invalid_url"
#    )

    gear = Gear(
            name = name,
            variant = variant,
            brand_id = brand,
            size = size,
            mass_pcs = mass_pcs,
            price = price,
            amount = amount,
            color = color,
            category_id = category,
            description = description,
            prod_date = prod_date,
            checked = False,
            last_checked = None,
            lifespan = lifespan,
            kit_only = kit_only,
    )

    if gear.name:
        db.add_gear(gear)
        print(lang.t("gear_functions.msg.gear_added"))
    else:
        print(lang.t("gear-functions.error.no_name"))

