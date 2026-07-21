import sqlite3
from pathlib import Path

from app.config_manager import ConfigManager
from app.lang import lang
from app.data import db
from app.data.db import add_gear, get_gear_by_id
from app.core.utils.validation import prompt_validated_input, is_positive_number, is_valid_date, is_nonempty_string, is_positive_integer_or_empty, is_yes_no
from app.core.utils.db_utils import fuzzy_search
from app.core.gear_item import Gear
from app.cli.brand_functions import list_brands
from app.cli.category_functions import pick_category
from app.cli.comment_functions import list_comments
from app.cli.cli_utils import paged_list, print_header, show_diff, prompt_field, fuzzy_pick, list_pick, confirm, print_table

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

    category = pick_category()


    description = input(f"{lang.t('gear_functions.cli.gear_description')}").strip()

    prod_date = prompt_validated_input(
        prompt_key="gear_functions.cli.gear_prod_date",
        validator=is_valid_date,
        allow_empty=True,
        error_key="gear_functions.error.not_valid"
    )

    lifespan = prompt_validated_input(
        prompt_key = "gear_functions.cli.gear_lifespan",
        validator  = is_positive_integer_or_empty,
        allow_empty= True,
        error_key  = "gear_functions.error.not_number"
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

    print(gear)

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
    "brand":       "gear_functions.fields.brand",
    "size":        "gear_functions.fields.size",
    "mass_pcs":    "gear_functions.fields.mass",
    "amount":      "gear_functions.fields.amount",
    "color":       "gear_functions.fields.color",
    "category_id": "gear_functions.fields.category",
}

def _get_category_name(category_id):
    """Get category name by ID."""
    if not category_id:
        return "—"
    cat = db.get_category_by_id(category_id)
    return cat.name if cat else "—"


def edit_gear():
    print(lang.t("edit_functions.title.edit_gear"))
    row = fuzzy_pick("Gear", "user_db", ["id_gear", "name", "variant"], ["ID", "Name", "Variant"])
    if not row:
        return

    gear = db.get_gear_by_id(row["id_gear"])
    if not gear:
        print(lang.t("edit_functions.error.not_found"))
        return

    fields = [
        ("name",        "gear_functions.fields.name",     gear.name,        is_nonempty_string, None),
        ("variant",     "gear_functions.fields.variant",  gear.variant,     None, None),
        ("brand_id",    "gear_functions.fields.brand",    gear.brand.name if gear.brand else "—",    None, gear.brand_id),
        ("category_id", "gear_functions.fields.category", _get_category_name(gear.category_id), None, gear.category_id),
        ("size",        "gear_functions.fields.size",     gear.size,        None, None),
        ("color",       "gear_functions.fields.color",    gear.color,       None, None),
        ("mass_pcs",    "gear_functions.fields.mass",     gear.mass_pcs,    is_positive_number, None),
        ("amount",      "gear_functions.fields.amount",   gear.amount,      is_positive_number, None),
        ("price",       "gear_functions.fields.price",    gear.price,       is_positive_number, None),
        ("lifespan",    "gear_functions.fields.lifespan", gear.lifespan,    is_positive_integer_or_empty, None),
        ("description", "gear_functions.fields.description", gear.description, None, None),
        ("kit_only",    "gear_functions.fields.kit_only", gear.kit_only,    is_yes_no, None),
    ]

    while True:
        print()
        for i, (_, t_key, current, _v, _id) in enumerate(fields, 1):
            print(f"  {i:<3} {lang.t(t_key):<16}: {current}")
        print(f"  S. Save    D. Discard")

        choice = input(lang.t("edit_functions.cli.pick_field")).strip().upper()

        if choice == "D":
            print(lang.t("edit_functions.msg.discarded"))
            return
        if choice == "S":
            break
        if choice.isdigit() and 0 <= int(choice) - 1 < len(fields):
            idx = int(choice) - 1
            key, t_key, current, validator, original_id = fields[idx]
            

            if key == "brand_id":
                new_val = _pick_brand_for_edit()
                if new_val is not None:
                    new_id = new_val["id_brand"]  # Extract the new ID
                    fields[idx] = (key, t_key, new_val["name"], validator, new_id)
            elif key == "category_id":
                new_val = _pick_category_for_edit()
                if new_val is not None:
                    new_id = new_val["id_category"]  # Extract the new ID
                    fields[idx] = (key, t_key, new_val["name"], validator, new_id)
            else:
                new_val = prompt_field(lang.t(t_key), current, validator)
                fields[idx] = (key, t_key, new_val, validator, original_id)

    # Build diff and apply
    original = db.get_gear_by_id(gear.id_gear)
    
    # Auto-generate orig_vals from fields
    orig_vals = {key: getattr(original, key) for key, _, _, _, _ in fields}
    # But for brand and category, show the names not IDs

    if original.brand:
        orig_vals["brand_id"] = original.brand.name
    if original.category_id:
        orig_vals["category_id"] = original.category_id


    changes = {}
    for key, t_key, new_val, validator, original_id in fields:
        old_val = orig_vals.get(key)
        
        # For brand_id and category_id, handle specially
        if key in ("brand_id", "category_id"):
            if isinstance(new_val, dict):
                # User picked a new one
                id_key = "id_brand" if key == "brand_id" else "id_category"
                new_id = new_val[id_key]
            else:
                new_id = original_id

            setattr(gear, key, new_id)

            if new_val != old_val:
                changes[t_key] = (old_val, new_val)
        else:
            setattr(gear, key, new_val)

            if new_val != old_val:
                changes[t_key] = (old_val, new_val)

    show_diff(changes)
    if not changes:
        return
    if confirm("edit_functions.cli.confirm_save"):
        db.update_gear(gear)
        print(lang.t("edit_functions.msg.saved"))
    else:
        print(lang.t("edit_functions.msg.discarded"))


def display_full_gear(gear: Gear):  # receives Gear object directly
    """Print all fields of a single gear item."""
    f = "gear_functions.fields"
    print(lang.t("gear_functions.title.full_gear"))
    print("=" * 40)
    print(f"  {gear.name}  —  {gear.variant or '—'}")
    print("=" * 40)
    print(f"  {lang.t(f+'.id'):<14}: {gear.id_gear}")
    print(f"  {lang.t(f+'.brand'):<14}: {gear.brand.name}")
    print(f"  {lang.t(f+'.category'):<14}: {gear.category.name}")
    print(f"  {lang.t(f+'.size'):<14}: {gear.size or '—'}")
    print(f"  {lang.t(f+'.color'):<14}: {gear.color or '—'}")
    print(f"  {lang.t(f+'.mass'):<14}: {gear.mass_pcs or '—'}")
    print(f"  {lang.t(f+'.amount'):<14}: {gear.amount or '—'}")
    print(f"  {lang.t(f+'.price'):<14}: {gear.price}") # FIX price
    print(f"  {lang.t(f+'.prod_date'):<14}: {gear.prod_date or '—'}")
    print(f"  {lang.t(f+'.lifespan'):<14}: {gear.lifespan or '∞'}")
    print(f"  {lang.t(f+'.kit_only'):<14}: {gear.kit_only}")
    print(f"  {lang.t(f+'.checked'):<14}: {'Yes' if gear.checked else 'No'}")
    print(f"  {lang.t(f+'.last_checked'):<14}: {gear.last_checked or '—'}")
    print(f"  {lang.t(f+'.description'):<14}: {gear.description or '—'}")
    print()

def list_gear(page_size: int = 10):
    """Paginated gear list with drill-down to full detail and comments."""
    def on_select(item):
        display_full_gear(item["id_gear"])
        list_comments(item["id_gear"])
        input(lang.t("gear_functions.msg.enter_to_return"))

    paged_list(
        items        = db.get_all_gear(),
        columns      = GEAR_LIST_COLUMNS,
        default_cols = ["name", "variant", "size", "amount"],
        on_select    = lambda g: display_full_gear(g),
        page_size    = page_size,
        title_key    = "gear_functions.title.list_gear",
        empty_key    = "gear_functions.error.no_gear",
    )


def delete_gear():
    print(lang.t("delete_functions.title.delete_gear"))
    row = fuzzy_pick("Gear", "user_db", ["id_gear", "name", "variant"], ["ID", "Name", "Variant"])
    if not row:
        return

    kit_count  = count_kit_references(row["id_gear"])
    trip_count = count_trip_references_gear(row["id_gear"])

    if kit_count:
        print(lang.t("delete_functions.msg.warn_kits", count=kit_count))
    if trip_count:
        print(lang.t("delete_functions.msg.warn_trips", count=trip_count))
    if not confirm("delete_functions.msg.confirm", name=row["name"]):
        print(lang.t("delete_functions.msg.cancelled"))
        return

    db.delete_gear(row["id_gear"])
    print(lang.t("delete_functions.msg.deleted", name=row["name"]))


def _pick_brand_for_edit() -> dict | None:
    """Let user search and pick a brand, return dict with id_brand and name."""
    from app.core.utils.db_utils import fuzzy_search
    
    term = input(f"{lang.t('gear_functions.cli.search_brand')}").strip()
    if not term:
        return None

    results = fuzzy_search(
        table="Brand",
        search_columns="name",
        search_term=term,
        return_columns=["id_brand", "name"],
        sort_by="name",
        db_name="program_db",
    ) or []

    if not results:
        print(lang.t("delete_functions.error.not_found"))
        return None

    # Convert to objects for print_table
    class BrandResult:
        def __init__(self, idx, **kwargs):
            self._idx = idx
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    numbered = [BrandResult(i + 1, **r) for i, r in enumerate(results)]
    print_table(
        items=numbered,
        columns=["_idx", "id_brand", "name"],
        labels=["#", "ID", "Name"],
    )

    raw = input(lang.t("menu.cli.prompt") + " ").strip()
    if not raw.isdigit() or not (0 <= int(raw) - 1 < len(results)):
        print(lang.t("delete_functions.error.invalid_choice"))
        return None

    return results[int(raw) - 1]


def _pick_category_for_edit() -> dict | None:
    """Let user search and pick a category, return dict with id_category and name."""
    categories = db.get_all_categories()
    
    if not categories:
        print(lang.t("delete_functions.error.not_found"))
        return None

    # Convert to objects for print_table
    class CategoryResult:
        def __init__(self, idx, id_category, category, description):
            self._idx = idx
            self.id_category = id_category
            self.name = category
            self.description = description
    
    numbered = [
        CategoryResult(i + 1, cat[0], cat[1], cat[2]) 
        for i, cat in enumerate(categories)
    ]
    
    print_table(
        items=numbered,
        columns=["_idx", "id_category", "name"],
        labels=["#", "ID", "Name"],
    )

    raw = input(lang.t("menu.cli.prompt") + " ").strip()
    if not raw.isdigit() or not (0 <= int(raw) - 1 < len(categories)):
        print(lang.t("delete_functions.error.invalid_choice"))
        return None

    cat = categories[int(raw) - 1]
    return {"id_category": cat[0], "name": cat[1]}
