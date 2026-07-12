import json
from app.lang import lang
from app.data import db
from app.core.utils.db_utils import fuzzy_search
from app.core.utils.validation import (
    prompt_validated_input, is_positive_integer, is_valid_month, is_valid_tags
)
from app.core.trip import Trip
from app.core.gear_item import Gear
from app.core.kit_item import Kit
from app.cli.cli_utils import paged_list, print_table, show_diff, prompt_field
from app.cli.comment_functions import list_comments


TRIP_LIST_COLUMNS = {
    "id_trip":    "trip_functions.fields.id",
    "name":       "trip_functions.fields.name",
    "month":      "trip_functions.fields.month",
    "duration":   "trip_functions.fields.duration",
    "no_people":  "trip_functions.fields.no_people",
    "total_mass": "trip_functions.fields.total_mass",
}

DEFAULT_TRIP_COLS = ["id_trip", "name", "month", "duration", "total_mass"]


def _month_name(month: int | str | None) -> str:
    """Convert month number to localized name."""
    if month is None:
        return "—"
    return lang.t(f"trip_functions.months.{int(month)}")


def _trips_to_display_rows(trips: list[Trip]) -> list[dict]:
    return [
        {
            "id_trip":    t.id_trip,
            "name":       t.name,
            "month":      _month_name(t.trip_month),
            "duration":   t.duration,
            "no_people":  t.no_people,
            "total_mass": t.total_mass(),
        }
        for t in trips
    ]

def _count_trip_references_gear(gear_id: int) -> int:
    """Count how many trips reference this gear."""
    trips = db.get_all_trips()
    return sum(
        1 for t in trips
        if any(hasattr(item, "id_gear") and item.id_gear == gear_id for item in t.items)
    )


def _count_trip_references_kit(kit_id: int) -> int:
    """Count how many trips reference this kit."""
    trips = db.get_all_trips()
    return sum(
        1 for t in trips
        if any(hasattr(item, "id_kit") and item.id_kit == kit_id for item in t.items)
    )


# -----------------------------------------------
# Item selection (gear + kits combined)
# -----------------------------------------------

def _search_items(term: str) -> list[dict]:
    """Search gear and kits simultaneously, return combined list with type marker."""
    gear_results = fuzzy_search(
        table          = "Gear",
        search_columns = "name",
        search_term    = term,
        return_columns = ["id_gear", "name", "variant", "mass_pcs"],
        sort_by        = "name",
        db_name        = "user_db",
    ) or []

    kit_results = fuzzy_search(
        table          = "Kit",
        search_columns = "name",
        search_term    = term,
        return_columns = ["id_kit", "name", "description"],
        sort_by        = "name",
        db_name        = "user_db",
    ) or []

    combined = []
    for r in gear_results:
        combined.append({
            "ref":     f"G:{r['id_gear']}",
            "marker":  "[G]",
            "name":    r.get("name", ""),
            "detail":  r.get("variant") or "—",
            "mass":    r.get("mass_pcs") or "—",
        })
    for r in kit_results:
        combined.append({
            "ref":     f"K:{r['id_kit']}",
            "marker":  "[K]",
            "name":    r.get("name", ""),
            "detail":  r.get("description") or "—",
            "mass":    "—",
        })
    return combined


def _pick_item() -> tuple | None:
    """Search gear+kits, let user pick one and enter amount."""
    term = input(lang.t("trip_functions.cli.search_items")).strip()
    if not term:
        return None

    results = _search_items(term)
    if not results:
        print(lang.t("trip_functions.error.no_results"))
        return None

    numbered = [{**r, "idx": i+1} for i, r in enumerate(results)]
    print_table(
        items   = numbered,
        columns = ["idx", "marker", "name", "detail", "mass"],
        labels  = ["#", "Type", "Name", "Variant/Desc", "Mass(g)"],
    )

    raw = input(lang.t("trip_functions.cli.select_item")).strip()
    if not raw.isdigit() or not (0 <= int(raw) - 1 < len(results)):
        print(lang.t("trip_functions.error.invalid_selection"))
        return None

    chosen = results[int(raw) - 1]
    ref    = chosen["ref"]

    raw_amt = input(lang.t("trip_functions.cli.item_amount")).strip()
    amount  = int(raw_amt) if raw_amt.isdigit() and int(raw_amt) > 0 else 1

    if ref.startswith("K:"):
        obj = db.get_kit_by_id(int(ref[2:]))
    else:
        obj = db.get_gear_by_id(int(ref[2:]))

    return obj, amount


def _show_current_items(trip: Trip):
    if not trip.items:
        print(f"  {lang.t('trip_functions.msg.no_items_added')}")
        return
    print(lang.t("trip_functions.msg.current_items"))
    for item, amt in zip(trip.items, trip.item_amounts):
        marker = "[K]" if isinstance(item, Kit) else "[G]"
        mass   = item.total_mass() if isinstance(item, Kit) else (item.mass_pcs or 0) * amt
        print(f"  {marker} {item.name}  x{amt}  — {mass}g")


# -----------------------------------------------
# Consumable selection
# -----------------------------------------------

def _search_consumables(term: str) -> list[dict]:
    results = fuzzy_search(
        table          = "consumable",
        search_columns = "name",
        search_term    = term,
        return_columns = ["id_consumable", "name", "description", "weight"],
        sort_by        = "name",
        db_name        = "program_db",
    ) or []
    return results


def _pick_consumable() -> tuple | None:
    """Search consumables, let user pick one and enter amount."""
    term = input(lang.t("trip_functions.cli.search_consumable")).strip()
    if not term:
        return None

    results = _search_consumables(term)
    if not results:
        print(lang.t("trip_functions.error.no_results"))
        return None

    numbered = [{**r, "idx": i+1} for i, r in enumerate(results)]
    print_table(
        items   = numbered,
        columns = ["idx", "id_consumable", "name", "description", "weight"],
        labels  = ["#", "ID", "Name", "Description", "Weight(g)"],
    )

    raw = input(lang.t("trip_functions.cli.select_item")).strip()
    if not raw.isdigit() or not (0 <= int(raw) - 1 < len(results)):
        print(lang.t("trip_functions.error.invalid_selection"))
        return None

    chosen = results[int(raw) - 1]

    raw_amt = input(lang.t("trip_functions.cli.item_amount")).strip()
    amount  = int(raw_amt) if raw_amt.isdigit() and int(raw_amt) > 0 else 1

    # wrap consumable as Gear-like for Trip model
    g = Gear(
        name        = chosen["name"],
        variant     = "",
        mass_pcs    = chosen.get("weight"),
        description = chosen.get("description"),
    )
    g.id_consumable = chosen["id_consumable"]
    return g, amount


def _show_current_consumables(trip: Trip):
    if not trip.consumables:
        print(f"  {lang.t('trip_functions.msg.no_consumables')}")
        return
    print(lang.t("trip_functions.msg.current_consumables"))
    for con, amt in zip(trip.consumables, trip.consumable_amounts):
        mass = (con.mass_pcs or 0) * amt
        print(f"  {con.name}  x{amt}  — {mass}g")


# -----------------------------------------------
# Display
# -----------------------------------------------

def display_full_trip(trip: Trip):
    """Print full trip detail."""
    print(lang.t("trip_functions.title.trip_detail"))
    print("=" * 40)
    print(f"  {trip.name}")
    if trip.description:
        print(f"  {trip.description}")
    print("=" * 40)
    if trip.tags:
        print(f"  {lang.t('trip_functions.fields.tags')}: {', '.join(trip.tags)}")
    print(f"  {lang.t('trip_functions.fields.month')}   : {_month_name(trip.trip_month)}")
    print(f"  {lang.t('trip_functions.fields.duration')} : {trip.duration}d")
    print(f"  {lang.t('trip_functions.fields.no_people')}: {trip.no_people}")
    print()

    # Gear & kits
    print(lang.t("trip_functions.msg.gear_section"))
    gear_rows = []
    for item, amt in zip(trip.items, trip.item_amounts):
        if isinstance(item, Kit):
            mass = item.total_mass() * amt
            gear_rows.append({"marker": "[K]", "name": item.name, "variant": "—", "amount": amt, "mass": f"{mass}g"})
        else:
            mass = (item.mass_pcs or 0) * amt
            gear_rows.append({"marker": "[G]", "name": item.name, "variant": item.variant or "—", "amount": amt, "mass": f"{mass}g"})

    print_table(
        items   = gear_rows,
        columns = ["marker", "name", "variant", "amount", "mass"],
        labels  = ["Type", "Name", "Variant", "Qty", "Mass"],
    )
    print(f"  {lang.t('trip_functions.msg.mass_correction', correction=trip.gear_mass_correction)}")
    print(f"  {lang.t('trip_functions.msg.gear_mass', mass=trip.gear_mass())}")
    print()

    # Consumables
    print(lang.t("trip_functions.msg.consumable_section"))
    con_rows = [
        {"name": c.name, "amount": amt, "mass": f"{(c.mass_pcs or 0) * amt}g"}
        for c, amt in zip(trip.consumables, trip.consumable_amounts)
    ]
    print_table(
        items   = con_rows,
        columns = ["name", "amount", "mass"],
        labels  = ["Name", "Qty", "Mass"],
    )
    print(f"  {lang.t('trip_functions.msg.mass_correction', correction=trip.consumable_mass_correction)}")
    print(f"  {lang.t('trip_functions.msg.consumable_mass', mass=trip.consumable_mass())}")
    print()
    print(f"  {lang.t('trip_functions.msg.total_mass', mass=trip.total_mass())}")
    print()


# -----------------------------------------------
# Input & list
# -----------------------------------------------

def input_trip():
    """Walk the user through creating a new trip."""
    print(lang.t("trip_functions.title.new_trip"))

    name = input(lang.t("trip_functions.cli.trip_name")).strip()
    if not name:
        print(lang.t("trip_functions.error.no_name"))
        return

    description = input(lang.t("trip_functions.cli.trip_description")).strip()

    raw_tags = prompt_validated_input(
        prompt_key = "trip_functions.cli.trip_tags",
        validator  = is_valid_tags,
        allow_empty= True,
        error_key  = "trip_functions.error.invalid_tags",
    )

    trip_month = prompt_validated_input(
        prompt_key = "trip_functions.cli.trip_month",
        validator  = is_valid_month,
        allow_empty= True,
        error_key  = "trip_functions.error.invalid_month",
    )

    duration = prompt_validated_input(
        prompt_key = "trip_functions.cli.duration",
        validator  = is_positive_integer,
        allow_empty= True,
        error_key  = "trip_functions.error.invalid_integer",
    )

    max_altitude = prompt_validated_input(
        prompt_key = "trip_functions.cli.max_altitude",
        validator  = is_positive_integer,
        allow_empty= True,
        error_key  = "trip_functions.error.invalid_integer",
    )

    no_people = prompt_validated_input(
        prompt_key = "trip_functions.cli.no_people",
        validator  = is_positive_integer,
        allow_empty= True,
        error_key  = "trip_functions.error.invalid_integer",
    )

    trip = Trip(
        id_trip      = None,
        name         = name,
        description  = description,
        tags = raw_tags or [],
        trip_month   = trip_month,
        duration     = duration or 0,
        max_altitude = max_altitude,
        no_people    = no_people or 1,
    )

    # Gear & kit selection
    print(lang.t("trip_functions.title.gear_selection"))
    while True:
        print()
        _show_current_items(trip)
        cont = input(lang.t("trip_functions.cli.continue_items")).strip().lower()
        if cont not in ("y", "yes"):
            break
        result = _pick_item()
        if result:
            obj, amount = result
            trip.add_item(obj, amount)
            print(lang.t("trip_functions.msg.item_added", name=obj.name, amount=amount))

    raw_corr = input(lang.t("trip_functions.cli.mass_correction")).strip()
    try:
        trip.gear_mass_correction = int(raw_corr)
    except ValueError:
        trip.gear_mass_correction = 0

    # Consumable selection
    print(lang.t("trip_functions.title.consumable_selection"))
    while True:
        print()
        _show_current_consumables(trip)
        cont = input(lang.t("trip_functions.cli.continue_consumables")).strip().lower()
        if cont not in ("y", "yes"):
            break
        result = _pick_consumable()
        if result:
            con, amount = result
            trip.add_consumable(con, amount)
            print(lang.t("trip_functions.msg.item_added", name=con.name, amount=amount))

    raw_corr = input(lang.t("trip_functions.cli.consumable_mass_correction")).strip()
    try:
        trip.consumable_mass_correction = int(raw_corr)
    except ValueError:
        trip.consumable_mass_correction = 0

    trip_id = db.add_trip(trip)
    print(lang.t("trip_functions.msg.trip_saved", name=name))
    display_full_trip(db.get_trip_by_id(trip_id))

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


def list_trips():
    """Paged list of all trips."""
    trips = db.get_all_trips()

    def on_select(item):
        trip = db.get_trip_by_id(item["id_trip"])
        display_full_trip(trip)
        list_comments(item["id_trip"])
        input(lang.t("trip_functions.msg.enter_to_return"))

    paged_list(
        items        = _trips_to_display_rows(trips),
        columns      = TRIP_LIST_COLUMNS,
        default_cols = DEFAULT_TRIP_COLS,
        on_select    = on_select,
        title_key    = "trip_functions.title.list_trips",
        empty_key    = "trip_functions.error.no_results",
    )

def delete_trip():
    print(lang.t("delete_functions.title.delete_trip"))
    row = _fuzzy_pick("Trip", "user_db", ["id_trip", "name"], ["ID", "Name"])
    if not row:
        return

    if not confirm("delete_functions.msg.confirm", name=row["name"]):
        print(lang.t("delete_functions.msg.cancelled"))
        return

    db.delete_trip(row["id_trip"])
    print(lang.t("delete_functions.msg.deleted", name=row["name"]))

