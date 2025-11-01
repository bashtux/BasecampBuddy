import sqlite3
from pathlib import Path

from app.config_manager import ConfigManager
from app.lang import lang
from app.data import db

from app.core.utils.validation import prompt_validated_input, is_positive_number, is_valid_date, is_nonempty_string
from app.core.utils.db_utils import fuzzy_search
from app.core.gear_item import Gear
from app.cli.brand_functions import list_brands

#------------------------------
# Load config and language
#------------------------------

def input_gear():
    """
    Ask the user for a new gear and insert into user_db
    """

    print(lang.t("gear_functions.title.new_gear"))
    name = prompt_validated_input(
            prompt_key="gear_functions.cli.gear_name",
            validator=is_nonempty_string,
            allow_empty=False,
            error_key="gear_functions.error.is_empty"
    )

    variant = input(f"{lang.t('gear_functions.cli.gear_variant')}").strip()

    brand = input(f"{lang.t('gear_functions.cli.search_brand')}").strip()
    brand_search = fuzzy_search (
            table="brand",
            search_columns="name",
            search_term=brand,
            return_columns=["id_brand", "name"],
            sort_by="name",
            db_name="program_db"
        )
    list_brands(brand_search, ["id_brand", "name"])
    brand_id = input(f"{lang.t('gear_functions.cli.select_brand')}").strip()


    size = input(f"{lang.t('gear_functions.cli.gear_size')}").strip()

    mass_pcs = prompt_validated_input(
            prompt_key="gear_functions.cli.gear_mass_pcs",
            validator=is_positive_number,
            allow_empty=True,
            error_key="gear_functions.error.not_number"
    )

    price = prompt_validated_input(
            prompt_key="gear_functions.cli.gear_price",
            validator=is_positive_number,
            allow_empty=True,
            error_key="gear_functions.error.not_number"
    )

    amount = prompt_validated_input(
            prompt_key="gear_functions.cli.gear_amount",
            validator=is_positive_number,
            allow_empty=True,
            error_key="gear_functions.error.not_number"
    )

    color = input(f"{lang.t('gear_functions.cli.gear_color')}").strip()

    category = input(f"{lang.t('gear_functions.cli.search_category')}").strip()

    description = input(f"{lang.t('gear_functions.cli.gear_description')}").strip()

    prod_date = prompt_validated_input(
        prompt_key="gear_functions.cli.gear_prod_date",
        validator=is_valid_date,
        allow_empty=True,
        error_key="gear_functions.error.not_valid"
    )

    lifespan = prompt_validated_input(
            prompt_key="gear_functions.cli.gear_lifespan",
            validator=is_positive_number,
            allow_empty=True,
            error_key="gear_functions.error.not_number"
    )

    kit_only = prompt_validated_input(
            prompt_key="gear_functions.cli.gear_kit_only",
            validator=is_yes_no,
            allow_empty=False,
            error_key="gear_functions.error.not_yes_no"
    )

    gear = Gear(
            name = name,
            variant = variant,
            brand_id = brand_id,
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
            kit_only = int(kit_only)
    )

    if gear.name:
        db.add_gear(gear)
        print(lang.t("gear_functions.msg.gear_added").format(gear_name=gear.name))
    else:
        print(lang.t("gear_functions.error.no_name"))

