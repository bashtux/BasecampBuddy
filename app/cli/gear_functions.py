import sqlite3
from pathlib import Path

from app.config_manager import ConfigManager
from app.lang import lang
from app.data import db

from app.core.utils.validation import prompt_validated_input, is_positive_number, is_valid_date, is_nonempty_string
from app.core.utils.db_utils import fuzzy_search
from app.core.gear_item import Gear
from app.cli.brand_functions import list_brands
from app.data import user_db as db
from app.cli.comment_functions import list_comments
from app.cli.cli_utils import paged_list, print_header

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

# column key -> translation key (resolved via lang.t() at display time)
GEAR_LIST_COLUMNS = {
    "id_gear":     "gear_functions.fields.id",
    "name":        "gear_functions.fields.name",
    "variant":     "gear_functions.fields.variant",
    "brand_id":    "gear_functions.fields.brand",
    "size":        "gear_functions.fields.size",
    "mass_pcs":    "gear_functions.fields.mass",
    "amount":      "gear_functions.fields.amount",
    "color":       "gear_functions.fields.color",
    "category_id": "gear_functions.fields.category",
}

DEFAULT_LIST_COLS = ["id_gear", "name", "variant", "size", "mass_pcs"]


def display_full_gear(gear: dict):
    """Print all fields of a single gear item."""
    g = dict(gear)
    f = "gear_functions.fields"
    print(lang.t("gear_functions.title.full_gear"))
    print("=" * 40)
    print(f"  {g.get('name', '—')}  —  {g.get('variant', '—')}")
    print("=" * 40)
    print(f"  {lang.t(f+'.id'):<14}: {g.get('id_gear')}")
    print(f"  {lang.t(f+'.brand'):<14}: {g.get('brand_id') or '—'}")
    print(f"  {lang.t(f+'.category'):<14}: {g.get('category_id') or '—'}")
    print(f"  {lang.t(f+'.size'):<14}: {g.get('size') or '—'}")
    print(f"  {lang.t(f+'.color'):<14}: {g.get('color') or '—'}")
    print(f"  {lang.t(f+'.mass'):<14}: {g.get('mass_pcs') or '—'}")
    print(f"  {lang.t(f+'.amount'):<14}: {g.get('amount') or '—'}")
    price = g.get('price_cents')
    print(f"  {lang.t(f+'.price'):<14}: {price / 100:.2f}" if price else f"  {lang.t(f+'.price'):<14}: —")
    print(f"  {lang.t(f+'.prod_date'):<14}: {g.get('prod_date') or '—'}")
    print(f"  {lang.t(f+'.lifespan'):<14}: {g.get('lifespan') or '∞'}")
    print(f"  {lang.t(f+'.kit_only'):<14}: {g.get('kit_only') or '—'}")
    print(f"  {lang.t(f+'.checked'):<14}: {'Yes' if g.get('checked') else 'No'}")
    print(f"  {lang.t(f+'.last_checked'):<14}: {g.get('last_checked') or '—'}")
    print(f"  {lang.t(f+'.description'):<14}: {g.get('description') or '—'}")
    print()

def list_gear(page_size: int = 10):
    """Paginated gear list with drill-down to full detail and comments."""
    def on_select(item):
        display_full_gear(item)
        list_comments(item["id_gear"])
        input(lang.t("gear_functions.msg.enter_to_return"))

    paged_list(
        items        = db.get_all_gear(),
        columns      = GEAR_LIST_COLUMNS,
        default_cols = DEFAULT_LIST_COLS,
        on_select    = on_select,
        page_size    = page_size,
        title_key    = "gear_functions.title.list_gear",
        empty_key    = "gear_functions.error.no_gear",
    )

