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


def _pick_list_columns() -> list[str]:
    """Interactively toggle which columns appear in list view."""
    selected = list(DEFAULT_LIST_COLS)
    while True:
        print(f"\n{lang.t('gear_functions.nav.toggle_hint')}")
        for i, (key, t_key) in enumerate(GEAR_LIST_COLUMNS.items(), 1):
            marker = "*" if key in selected else " "
            print(f"  {i}: [{marker}] {lang.t(t_key)}")
        print(f"  {lang.t('gear_functions.nav.confirm')}")

        choice = input(lang.t("gear_functions.cli.toggle_columns")).strip().upper()
        if choice == "C":
            return selected if selected else list(DEFAULT_LIST_COLS)
        if choice.isdigit():
            idx = int(choice) - 1
            keys = list(GEAR_LIST_COLUMNS.keys())
            if 0 <= idx < len(keys):
                key = keys[idx]
                if key in selected:
                    selected.remove(key)
                else:
                    selected.append(key)
            else:
                print(lang.t("gear_functions.error.invalid_selection"))
        else:
            print(lang.t("gear_functions.error.invalid_selection"))


def list_gear(page_size: int = 10, columns: list[str] | None = None):
    """Paginated gear list with selectable columns and drill-down to full detail."""
    if columns is None:
        columns = list(DEFAULT_LIST_COLS)

    all_gear = db.get_all_gear()
    if not all_gear:
        print(lang.t("gear_functions.error.no_gear"))
        return

    total = len(all_gear)
    page = 0

    while True:
        start = page * page_size
        end   = min(start + page_size, total)
        page_items = all_gear[start:end]
        total_pages = (total - 1) // page_size + 1

        print(lang.t("gear_functions.title.list_gear"))

        # header
        col_w  = max(12, 60 // len(columns))
        labels = [lang.t(GEAR_LIST_COLUMNS[c]) for c in columns]
        header = f"  {'#':<4}" + "".join(f"{lbl:<{col_w}}" for lbl in labels)
        print(header)
        print("  " + "-" * (len(header) - 2))

        for i, gear in enumerate(page_items, 1):
            g = dict(gear)
            row = f"  {i:<4}" + "".join(
                f"{str(g.get(c) or '—'):<{col_w}}" for c in columns
            )
            print(row)

        print(f"\n  {lang.t('gear_functions.msg.page_info', current=page+1, total=total_pages, count=total)}")
        print(f"  {lang.t('gear_functions.nav.next')}  "
              f"{lang.t('gear_functions.nav.prev')}  "
              f"{lang.t('gear_functions.nav.detail')}  "
              f"{lang.t('gear_functions.nav.columns')}  "
              f"{lang.t('gear_functions.nav.back')}")

        choice = input(lang.t("gear_functions.cli.select_item")).strip().upper()

        if choice == "N":
            if end < total:
                page += 1
            else:
                print(lang.t("gear_functions.msg.last_page"))
        elif choice == "P":
            if page > 0:
                page -= 1
            else:
                print(lang.t("gear_functions.msg.first_page"))
        elif choice == "C":
            columns = _pick_list_columns()
        elif choice == "B":
            return
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(page_items):
                display_full_gear(page_items[idx])
                list_comments(page_items[idx]["id_gear"])
                input(lang.t("gear_functions.msg.enter_to_return"))
            else:
                print(lang.t("gear_functions.error.invalid_selection"))
        else:
            print(lang.t("gear_functions.error.invalid_selection"))
