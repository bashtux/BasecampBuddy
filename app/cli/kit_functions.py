import json
from app.lang import lang
from app.data import db
from app.core.utils.db_utils import fuzzy_search
from app.core.kit_item import Kit
from app.cli.cli_utils import paged_list, print_table, show_diff, prompt_field
from app.cli.comment_functions import list_comments

KIT_LIST_COLUMNS = {
    "id_kit":     "kit_functions.fields.id",
    "name":       "kit_functions.fields.name",
    "item_count": "kit_functions.fields.item_count",
    "total_mass": "kit_functions.fields.total_mass",
}

DEFAULT_KIT_COLS = ["id_kit", "name", "item_count", "total_mass"]


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


def _count_kit_references(gear_id: int) -> int:
    """Count how many kits reference this gear."""
    kits = db.get_all_kits()
    return sum(1 for k in kits if gear_id in [g.id_gear for g in k.gear_list])


def display_full_kit(kit: Kit):
    """Print full detail of a kit."""
    print(lang.t("kit_functions.title.kit_detail"))
    print("=" * 40)
    print(f"  {kit.name}")
    if kit.description:
        print(f"  {kit.description}")
    print("=" * 40)

    # Create simple objects with the computed fields
    class GearDisplay:
        def __init__(self, name, variant, amount, mass):
            self.name = name
            self.variant = variant
            self.amount = amount
            self.mass = mass
    
    gear_rows = [
        GearDisplay(
            name=g.name,
            variant=g.variant or "—",
            amount=amt,
            mass=f"{(g.mass_pcs or 0) * amt}g",
        )
        for g, amt in zip(kit.gear_list, kit.gear_amount)
    ]

    print_table(
        items   = gear_rows,
        columns = ["name", "variant", "amount", "mass"],
        labels  = ["Name", "Variant", "Qty", "Mass"],
    )

    print()
    print(f"  {lang.t('kit_functions.msg.mass_correction', correction=kit.mass_correction)}")
    print(f"  {lang.t('kit_functions.msg.total_mass', mass=kit.total_mass)}")
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

    def on_select(item: Kit):
        display_full_kit(item)
        list_comments(item.id_kit)
        input(lang.t("kit_functions.msg.enter_to_return"))

    paged_list(
        items        = kits,
        columns      = KIT_LIST_COLUMNS,
        default_cols = DEFAULT_KIT_COLS,
        on_select    = on_select,
        title_key    = "kit_functions.title.list_kits",
        empty_key    = "kit_functions.error.no_kits",
        )

def edit_kit():
    print(lang.t("edit_functions.title.edit_kit"))
    row = _fuzzy_pick("Kit", "user_db", ["id_kit", "name"], ["ID", "Name"])
    if not row:
        return

    kit = db.get_kit_by_id(row["id_kit"])
    if not kit:
        print(lang.t("edit_functions.error.not_found"))
        return

    # Metadata fields
    fields = [
        ("name",            "kit_functions.fields.name",        kit.name,            is_nonempty_string),
        ("description",     "kit_functions.fields.description",  kit.description,     None),
        ("mass_correction", "kit_functions.fields.mass_correction", kit.mass_correction, None),
    ]

    while True:
        print()
        for i, (_, t_key, current, _v) in enumerate(fields, 1):
            print(f"  {i:<3} {lang.t(t_key):<20}: {current}")

        # Show gear items
        print(lang.t("edit_functions.title.gear_items"))
        if kit.gear_list:
            for i, (g, amt) in enumerate(zip(kit.gear_list, kit.gear_amount), 1):
                print(f"  G{i:<2} {g.name} {g.variant or ''}  x{amt}  — {(g.mass_pcs or 0)*amt}g")
        else:
            print("  (none)")

        print(f"\n  S. Save    D. Discard    A. Add gear    R. Remove gear")
        choice = input(lang.t("edit_functions.cli.pick_field")).strip().upper()

        if choice == "D":
            print(lang.t("edit_functions.msg.discarded"))
            return
        if choice == "S":
            break
        if choice == "A":
            result = _pick_gear()
            if result:
                g, amt = result
                kit.add_gear(g, amt)
                print(lang.t("edit_functions.msg.item_added", name=g.name))
        if choice == "R":
            raw = input(lang.t("edit_functions.cli.remove_item")).strip()
            if raw.startswith("G") and raw[1:].isdigit():
                idx = int(raw[1:]) - 1
                if 0 <= idx < len(kit.gear_list):
                    name = kit.gear_list[idx].name
                    kit.remove_gear(kit.gear_list[idx].id_gear)
                    print(lang.t("edit_functions.msg.item_removed", name=name))
        if choice.isdigit() and 0 <= int(choice) - 1 < len(fields):
            idx = int(choice) - 1
            key, t_key, current, validator = fields[idx]
            new_val = _prompt_field(lang.t(t_key), current, validator)
            fields[idx] = (key, t_key, new_val, validator)

    # Diff metadata only
    original = db.get_kit_by_id(kit.id_kit)
    orig_vals = {"name": original.name, "description": original.description, "mass_correction": original.mass_correction}
    changes = {}
    for key, t_key, new_val, _ in fields:
        old_val = orig_vals[key]
        if new_val != old_val:
            changes[t_key] = (old_val, new_val)
            setattr(kit, key, new_val)

    _show_diff(changes)
    if confirm("edit_functions.cli.confirm_save"):
        db.update_kit(kit)
        print(lang.t("edit_functions.msg.saved"))
    else:
        print(lang.t("edit_functions.msg.discarded"))


def delete_kit():
    print(lang.t("delete_functions.title.delete_kit"))
    row = _fuzzy_pick("Kit", "user_db", ["id_kit", "name"], ["ID", "Name"])
    if not row:
        return

    trip_count = _count_trip_references_kit(row["id_kit"])
    if trip_count:
        print(lang.t("delete_functions.msg.warn_trips", count=trip_count))

    if not confirm("delete_functions.msg.confirm", name=row["name"]):
        print(lang.t("delete_functions.msg.cancelled"))
        return

    db.delete_kit(row["id_kit"])
    print(lang.t("delete_functions.msg.deleted", name=row["name"]))

