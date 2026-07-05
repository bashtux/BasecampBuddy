import json
from app.lang import lang
from app.data import db
from app.core.utils.db_utils import fuzzy_search
from app.cli.cli_utils import confirm, print_table


# -----------------------------------------------
# Helpers
# -----------------------------------------------

def _fuzzy_pick(entity: str, db_name: str, columns: list[str], labels: list[str]) -> dict | None:
    """Fuzzy search an entity and return the chosen row as dict, or None."""
    term = input(f"Search {entity} (fuzzy): ").strip()
    if not term:
        return None

    results = fuzzy_search(
        table          = entity,
        search_columns = "name",
        search_term    = term,
        return_columns = columns,
        sort_by        = "name",
        db_name        = db_name,
    ) or []

    if not results:
        print(lang.t("delete_functions.error.not_found"))
        return None

    numbered = [{**r, "_idx": i + 1} for i, r in enumerate(results)]
    print_table(
        items   = numbered,
        columns = ["_idx"] + columns,
        labels  = ["#"] + labels,
    )

    raw = input(lang.t("menu.cli.prompt") + " ").strip()
    if not raw.isdigit() or not (0 <= int(raw) - 1 < len(results)):
        print(lang.t("delete_functions.error.invalid_choice"))
        return None

    return results[int(raw) - 1]


def _list_pick(items: list[tuple], columns: list[str], labels: list[str]) -> dict | None:
    """Show a simple list and let user pick by number."""
    if not items:
        print(lang.t("delete_functions.error.not_found"))
        return None

    rows = [dict(zip(columns, row)) for row in items]
    numbered = [{**r, "_idx": i + 1} for i, r in enumerate(rows)]
    print_table(
        items   = numbered,
        columns = ["_idx"] + columns,
        labels  = ["#"] + labels,
    )

    raw = input(lang.t("menu.cli.prompt") + " ").strip()
    if not raw.isdigit() or not (0 <= int(raw) - 1 < len(rows)):
        print(lang.t("delete_functions.error.invalid_choice"))
        return None

    return rows[int(raw) - 1]


def _count_kit_references(gear_id: int) -> int:
    """Count how many kits reference this gear."""
    kits = db.get_all_kits()
    return sum(1 for k in kits if gear_id in [g.id_gear for g in k.gear_list])


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
# Delete functions
# -----------------------------------------------

def delete_gear():
    print(lang.t("delete_functions.title.delete_gear"))
    row = _fuzzy_pick("Gear", "user_db", ["id_gear", "name", "variant"], ["ID", "Name", "Variant"])
    if not row:
        return

    kit_count  = _count_kit_references(row["id_gear"])
    trip_count = _count_trip_references_gear(row["id_gear"])

    if kit_count:
        print(lang.t("delete_functions.msg.warn_kits", count=kit_count))
    if trip_count:
        print(lang.t("delete_functions.msg.warn_trips", count=trip_count))
    if not confirm("delete_functions.msg.confirm", name=row["name"]):
        print(lang.t("delete_functions.msg.cancelled"))
        return

    db.delete_gear(row["id_gear"])
    print(lang.t("delete_functions.msg.deleted", name=row["name"]))


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


def delete_brand():
    print(lang.t("delete_functions.title.delete_brand"))
    row = _list_pick(
        db.get_all_brands(),
        ["id_brand", "name", "description"],
        ["ID", "Name", "Description"],
    )
    if not row:
        return

    if not confirm("delete_functions.msg.confirm"):
        print(lang.t("delete_functions.msg.cancelled"))
        return

    success = db.delete_brand(row["id_brand"])
    if success:
        print(lang.t("delete_functions.msg.deleted", name=row["name"]))
    else:
        print(lang.t("delete_functions.msg.has_references", name=row["name"]))


def delete_category():
    print(lang.t("delete_functions.title.delete_category"))
    row = _list_pick(
        db.get_all_categories(),
        ["id_category", "category", "description"],
        ["ID", "Name", "Description"],
    )
    if not row:
        return

    if not confirm("delete_functions.msg.confirm", name=row["name"]):
        print(lang.t("delete_functions.msg.cancelled"))
        return

    success = db.delete_category(row["id_category"])
    if success:
        print(lang.t("delete_functions.msg.deleted", name=row["category"]))
    else:
        print(lang.t("delete_functions.msg.has_references", name=row["category"]))


def delete_consumable():
    print(lang.t("delete_functions.title.delete_consumable"))
    row = _list_pick(
        db.get_all_consumables(),
        ["id_consumable", "name", "description"],
        ["ID", "Name", "Description"],
    )
    if not row:
        return

    if not confirm("delete_functions.msg.confirm", name=row["name"]):
        print(lang.t("delete_functions.msg.cancelled"))
        return

    success = db.delete_consumable(row["id_consumable"])
    if success:
        print(lang.t("delete_functions.msg.deleted", name=row["name"]))
    else:
        print(lang.t("delete_functions.msg.has_references", name=row["name"]))
