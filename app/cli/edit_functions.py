from app.lang import lang
from app.data import db
from app.core.gear_item import Gear
from app.core.kit_item import Kit
from app.core.trip import Trip
from app.core.utils.validation import (
    prompt_validated_input, is_nonempty_string, is_positive_number,
    is_positive_integer, is_valid_date, is_valid_url, is_yes_no,
    is_valid_month, is_valid_tags, is_positive_integer_or_empty,
)
from app.cli.cli_utils import confirm, print_table
from app.cli.delete_functions import _fuzzy_pick, _list_pick
from app.cli.kit_functions import _pick_gear, _show_current_gear
from app.cli.trip_functions import _pick_item, _pick_consumable, _month_name


# -----------------------------------------------
# Diff display
# -----------------------------------------------

def _show_diff(changes: dict):
    """Print only the changed fields."""
    if not changes:
        print(lang.t("edit_functions.title.no_changes"))
        return
    print(lang.t("edit_functions.title.changes"))
    for field, (old, new) in changes.items():
        print(f"  {lang.t(field)}: '{old}'  →  '{new}'")


def _prompt_field(label: str, current, validator=None, allow_empty=True):
    """
    Show current value, prompt for new one.
    Returns new value if changed, current value if Enter pressed.
    """
    raw = input(f"  {label} [{current}]: ").strip()
    if not raw:
        return current
    if validator:
        cleaned = validator(raw)
        if cleaned is None:
            print(lang.t("edit_functions.error.invalid_choice"))
            return current
        return cleaned
    return raw


# -----------------------------------------------
# Edit gear
# -----------------------------------------------

def edit_gear():
    print(lang.t("edit_functions.title.edit_gear"))
    row = _fuzzy_pick("Gear", "user_db", ["id_gear", "name", "variant"], ["ID", "Name", "Variant"])
    if not row:
        return

    gear = db.get_gear_by_id(row["id_gear"])
    if not gear:
        print(lang.t("edit_functions.error.not_found"))
        return

    fields = [
        ("name",        "gear_functions.fields.name",     gear.name,        is_nonempty_string),
        ("variant",     "gear_functions.fields.variant",  gear.variant,     None),
        ("brand_id",    "gear_functions.fields.brand",    gear.brand_id,    None),
        ("size",        "gear_functions.fields.size",     gear.size,        None),
        ("color",       "gear_functions.fields.color",    gear.color,       None),
        ("mass_pcs",    "gear_functions.fields.mass",     gear.mass_pcs,    is_positive_number),
        ("amount",      "gear_functions.fields.amount",   gear.amount,      is_positive_number),
        ("price",       "gear_functions.fields.price",    gear.price,       is_positive_number),
        ("lifespan",    "gear_functions.fields.lifespan", gear.lifespan,    is_positive_integer_or_empty),
        ("description", "gear_functions.fields.description", gear.description, None),
        ("kit_only",    "gear_functions.fields.kit_only", gear.kit_only,    is_yes_no),
    ]

    while True:
        print()
        for i, (_, t_key, current, _v) in enumerate(fields, 1):
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
            key, t_key, current, validator = fields[idx]
            new_val = _prompt_field(lang.t(t_key), current, validator)
            fields[idx] = (key, t_key, new_val, validator)

    # Build diff and apply
    original = db.get_gear_by_id(gear.id_gear)
    changes  = {}
    orig_vals = {
        "name": original.name, "variant": original.variant,
        "size": original.size, "color": original.color,
        "mass_pcs": original.mass_pcs, "amount": original.amount,
        "price": original.price, "lifespan": original.lifespan,
        "description": original.description, "kit_only": original.kit_only,
    }

    for key, t_key, new_val, _ in fields:
        old_val = orig_vals[key]
        if new_val != old_val:
            changes[t_key] = (old_val, new_val)
            setattr(gear, key, new_val)

    _show_diff(changes)
    if not changes:
        return

    if confirm("edit_functions.cli.confirm_save"):
        db.update_gear(gear)
        print(lang.t("edit_functions.msg.saved"))
    else:
        print(lang.t("edit_functions.msg.discarded"))


# -----------------------------------------------
# Edit kit
# -----------------------------------------------

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


# -----------------------------------------------
# Edit trip
# -----------------------------------------------

def edit_trip():
    print(lang.t("edit_functions.title.edit_trip"))
    row = _fuzzy_pick("Trip", "user_db", ["id_trip", "name"], ["ID", "Name"])
    if not row:
        return

    trip = db.get_trip_by_id(row["id_trip"])
    if not trip:
        print(lang.t("edit_functions.error.not_found"))
        return

    fields = [
        ("name",            "trip_functions.fields.name",       trip.name,            is_nonempty_string),
        ("description",     "gear_functions.fields.description", trip.description,     None),
        ("trip_month",      "trip_functions.fields.month",       trip.trip_month,      is_valid_month),
        ("duration",        "trip_functions.fields.duration",    trip.duration,        is_positive_integer),
        ("max_altitude",    "trip_functions.fields.no_people",   trip.max_altitude,    is_positive_integer),
        ("no_people",       "trip_functions.fields.no_people",   trip.no_people,       is_positive_integer),
        ("tags",            "trip_functions.fields.tags",        trip.tags,            is_valid_tags),
        ("gear_mass_correction",       "trip_functions.msg.mass_correction", trip.gear_mass_correction,       None),
        ("consumable_mass_correction", "trip_functions.msg.mass_correction", trip.consumable_mass_correction, None),
    ]

    while True:
        print()
        for i, (_, t_key, current, _v) in enumerate(fields, 1):
            print(f"  {i:<3} {lang.t(t_key):<24}: {current}")

        # Gear & kit items
        print(lang.t("edit_functions.title.gear_items"))
        if trip.items:
            for i, (item, amt) in enumerate(zip(trip.items, trip.item_amounts), 1):
                marker = "[K]" if isinstance(item, Kit) else "[G]"
                print(f"  I{i:<2} {marker} {item.name}  x{amt}")
        else:
            print("  (none)")

        # Consumables
        print(lang.t("edit_functions.title.consumables"))
        if trip.consumables:
            for i, (c, amt) in enumerate(zip(trip.consumables, trip.consumable_amounts), 1):
                print(f"  C{i:<2} {c.name}  x{amt}")
        else:
            print("  (none)")

        print(f"\n  S. Save    D. Discard    AI. Add item    RI. Remove item    AC. Add consumable    RC. Remove consumable")
        choice = input(lang.t("edit_functions.cli.pick_field")).strip().upper()

        if choice == "D":
            print(lang.t("edit_functions.msg.discarded"))
            return
        if choice == "S":
            break
        if choice == "AI":
            result = _pick_item()
            if result:
                obj, amt = result
                trip.add_item(obj, amt)
                print(lang.t("edit_functions.msg.item_added", name=obj.name))
        elif choice == "RI":
            raw = input(lang.t("edit_functions.cli.remove_item")).strip().upper()
            if raw.startswith("I") and raw[1:].isdigit():
                idx = int(raw[1:]) - 1
                if 0 <= idx < len(trip.items):
                    name = trip.items[idx].name
                    del trip.items[idx]
                    del trip.item_amounts[idx]
                    print(lang.t("edit_functions.msg.item_removed", name=name))
        elif choice == "AC":
            result = _pick_consumable()
            if result:
                c, amt = result
                trip.add_consumable(c, amt)
                print(lang.t("edit_functions.msg.item_added", name=c.name))
        elif choice == "RC":
            raw = input(lang.t("edit_functions.cli.remove_item")).strip().upper()
            if raw.startswith("C") and raw[1:].isdigit():
                idx = int(raw[1:]) - 1
                if 0 <= idx < len(trip.consumables):
                    name = trip.consumables[idx].name
                    del trip.consumables[idx]
                    del trip.consumable_amounts[idx]
                    print(lang.t("edit_functions.msg.item_removed", name=name))
        elif choice.isdigit() and 0 <= int(choice) - 1 < len(fields):
            idx = int(choice) - 1
            key, t_key, current, validator = fields[idx]
            new_val = _prompt_field(lang.t(t_key), current, validator)
            fields[idx] = (key, t_key, new_val, validator)

    # Diff metadata
    original  = db.get_trip_by_id(trip.id_trip)
    orig_vals = {
        "name": original.name, "description": original.description,
        "trip_month": original.trip_month, "duration": original.duration,
        "max_altitude": original.max_altitude, "no_people": original.no_people,
        "tags": original.tags, "gear_mass_correction": original.gear_mass_correction,
        "consumable_mass_correction": original.consumable_mass_correction,
    }
    changes = {}
    for key, t_key, new_val, _ in fields:
        old_val = orig_vals[key]
        if new_val != old_val:
            changes[t_key] = (old_val, new_val)
            setattr(trip, key, new_val)

    _show_diff(changes)
    if confirm("edit_functions.cli.confirm_save"):
        db.update_trip(trip)
        print(lang.t("edit_functions.msg.saved"))
    else:
        print(lang.t("edit_functions.msg.discarded"))


# -----------------------------------------------
# Edit brand, category, consumable
# (these already exist in their respective files
#  but are moved here for consistency)
# -----------------------------------------------

def edit_brand():
    from app.cli.brand_functions import edit_brand as _edit_brand
    _edit_brand()

def edit_category():
    from app.cli.category_functions import edit_category as _edit_category
    _edit_category()

def edit_consumable():
    from app.cli.consumable_functions import edit_consumable as _edit_consumable
    _edit_consumable()
