import json
from app.lang import lang
from app.data import db
from app.core.utils.db_utils import fuzzy_search
from app.core.utils.validation import (
    prompt_validated_input, is_positive_integer, is_valid_month
)
from app.core.trip import Trip
from app.core.gear_item import Gear
from app.core.kit_item import Kit
from app.cli.cli_utils import paged_list, print_table
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
