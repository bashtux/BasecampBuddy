import json
from app.lang import lang
from app.data import db
from app.core.utils.db_utils import fuzzy_search
from app.core.kit_item import Kit
from app.cli.cli_utils import paged_list, print_table
from app.cli.comment_functions import list_comments

KIT_LIST_COLUMNS = {
    "id_kit":     "kit_functions.fields.id",
    "name":       "kit_functions.fields.name",
    "item_count": "kit_functions.fields.item_count",
    "total_mass": "kit_functions.fields.total_mass",
}

DEFAULT_KIT_COLS = ["id_kit", "name", "item_count", "total_mass"]


def _kits_to_display_rows(kits: list[Kit]) -> list[dict]:
    """Convert Kit objects to display dicts with computed fields."""
    return [
        {
            "id_kit":     kit.id_kit,
            "name":       kit.name,
            "item_count": len(kit.gear_list),
            "total_mass": kit.total_mass(),
        }
        for kit in kits
    ]


def _pick_gear() -> tuple | None:
    """Fuzzy-search gear, let user pick one and enter amount."""
    term = input(lang.t("kit_functions.cli.search_gear")).strip()
    if not term:
        return None

    results = fuzzy_search(
        table          = "Gear",
        search_columns = "name",
        search_term    = term,
        return_columns = ["id_gear", "name", "variant", "mass_pcs", "amount"],
        sort_by        = "name",
        db_name        = "user_db",
    )

    if not results:
        print(lang.t("kit_functions.error.no_gear"))
        return None

    # Convert dicts to Gear objects and add index
    gear_objects = []
    for i, r in enumerate(results, 1):
        gear = db.get_gear_by_id(r["id_gear"])
        if gear:
            gear.idx = i  # add index as attribute
            gear_objects.append(gear)

    print_table(
        items   = gear_objects,
        columns = ["idx", "name", "variant", "mass_pcs", "amount"],
        labels  = ["#", "Name", "Variant", "Mass(g)", "Stock"],
    )

    raw = input(lang.t("kit_functions.cli.select_gear")).strip()
    if not raw.isdigit():
        print(lang.t("kit_functions.error.invalid_selection"))
        return None

    idx = int(raw) - 1
    if not (0 <= idx < len(results)):
        print(lang.t("kit_functions.error.invalid_selection"))
        return None

    gear = db.get_gear_by_id(results[idx]["id_gear"])
    if not gear:
        print(lang.t("kit_functions.error.no_gear"))
        return None

    raw_amt = input(lang.t("kit_functions.cli.gear_amount")).strip()
    amount  = int(raw_amt) if raw_amt.isdigit() and int(raw_amt) > 0 else 1

    if amount > (gear.amount or 0):
        print(lang.t("kit_functions.msg.amount_warning", available=gear.amount or 0))

    return gear, amount


def _show_current_gear(kit: Kit):
    """Print gear staged so far."""
    if not kit.gear_list:
        print(f"  {lang.t('kit_functions.msg.no_gear_added')}")
        return
    print(lang.t("kit_functions.msg.current_gear"))
    for gear, amt in zip(kit.gear_list, kit.gear_amount):
        mass = (gear.mass_pcs or 0) * amt
        print(f"  {gear.name} {gear.variant or ''}  x{amt}  — {mass}g")


def display_full_kit(kit: Kit):
    """Print full detail of a kit."""
    print(lang.t("kit_functions.title.kit_detail"))
    print("=" * 40)
    print(f"  {kit.name}")
    if kit.description:
        print(f"  {kit.description}")
    print("=" * 40)

    gear_rows = [
        {
            "name":    g.name,
            "variant": g.variant or "—",
            "amount":  amt,
            "mass":    f"{(g.mass_pcs or 0) * amt}g",
        }
        for g, amt in zip(kit.gear_list, kit.gear_amount)
    ]

    print_table(
        items   = gear_rows,
        columns = ["name", "variant", "amount", "mass"],
        labels  = ["Name", "Variant", "Qty", "Mass"],
    )

    print()
    print(f"  {lang.t('kit_functions.msg.mass_correction', correction=kit.mass_correction)}")
    print(f"  {lang.t('kit_functions.msg.total_mass', mass=kit.total_mass())}")
    print()


def input_kit():
    """Walk the user through creating a new kit and save it."""
    print(lang.t("kit_functions.title.new_kit"))

    name = input(lang.t("kit_functions.cli.kit_name")).strip()
    if not name:
        print(lang.t("kit_functions.error.no_name"))
        return

    description = input(lang.t("kit_functions.cli.kit_description")).strip()

    kit = Kit(id_kit=None, name=name, description=description)

    while True:
        print()
        _show_current_gear(kit)
        cont = input(lang.t("kit_functions.cli.continue")).strip().lower()
        if cont not in ("y", "yes"):
            break
        result = _pick_gear()
        if result:
            gear, amount = result
            kit.add_gear(gear, amount)
            print(lang.t("kit_functions.msg.gear_added", name=gear.name, amount=amount))

    raw_corr = input(lang.t("kit_functions.cli.mass_correction")).strip()
    try:
        kit.mass_correction = int(raw_corr)
    except ValueError:
        kit.mass_correction = 0

    kit_id = db.add_kit(kit)
    print(lang.t("kit_functions.msg.kit_saved", name=name))
    display_full_kit(db.get_kit_by_id(kit_id))


def list_kits():
    """Paged list of all kits."""
    kits = db.get_all_kits()

    def on_select(item):
        kit = db.get_kit_by_id(item["id_kit"])
        display_full_kit(kit)
        list_comments(item["id_kit"])
        input(lang.t("kit_functions.msg.enter_to_return"))

    paged_list(
        items        = _kits_to_display_rows(kits),
        columns      = KIT_LIST_COLUMNS,
        default_cols = DEFAULT_KIT_COLS,
        on_select    = on_select,
        title_key    = "kit_functions.title.list_kits",
        empty_key    = "kit_functions.error.no_kits",
    )
