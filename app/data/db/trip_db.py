import json
import sqlite3
from pathlib import Path
from typing import Union

from app.config_manager import ConfigManager
from app.core.trip import Trip
from app.core.gear_item import Gear
from app.core.kit_item import Kit
from app.data.db.gear_db import get_gear_by_id
from app.data.db.kit_db import get_kit_by_id

config = ConfigManager()
BASE_DIR = Path(__file__).resolve().parents[3]
user_db_rel = config.get("paths.user_db", "app/data/user_db.sqlite")
DB_PATH = (BASE_DIR / user_db_rel).resolve()
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def add_trip(trip: Trip) -> int:
    """Insert a new trip and return its ID."""
    # Store item IDs prefixed with type: "G:4" or "K:2"
    item_ids = []
    for item in trip.items:
        if isinstance(item, Kit):
            item_ids.append(f"K:{item.id_kit}")
        else:
            item_ids.append(f"G:{item.id_gear}")

    consumable_ids = [c.id_consumable for c in trip.consumables]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Trip (
            name, description, comment, tag, trip_month, duration,
            max_altitude, no_people, gear, gear_amount, gear_mass_correction,
            consumables, consumable_amount, consumable_mass_correction
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        trip.name,
        trip.description,
        json.dumps(trip.comments),
        json.dumps(trip.tags),
        int(trip.trip_month) if trip.trip_month else None,
        trip.duration,
        trip.max_altitude,
        trip.no_people,
        json.dumps(item_ids),
        json.dumps(trip.item_amounts),
        trip.gear_mass_correction,
        json.dumps(consumable_ids),
        json.dumps(trip.consumable_amounts),
        trip.consumable_mass_correction,
    ))
    trip_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return trip_id


def _load_consumable_as_gear(consumable_id: int) -> Gear | None:
    """Load a consumable from program_db and wrap it as a Gear-like object."""
    from app.data.db.program_db import get_consumable_by_id
    row = get_consumable_by_id(consumable_id)
    if not row:
        return None
    # consumable tuple: (id, name, description, weight)
    g = Gear(name=row[1], variant="", mass_pcs=row[3], description=row[2])
    g.id_consumable = row[0]
    return g


def get_trip_by_id(trip_id: int) -> Trip | None:
    """Fetch a single trip by ID, returning a Trip instance."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Trip WHERE id_trip = ?", (trip_id,))
        row = cursor.fetchone()
        if row is None:
            return None

    item_ids   = json.loads(row["gear"]             or "[]")
    amounts    = json.loads(row["gear_amount"]       or "[]")
    con_ids    = json.loads(row["consumables"]       or "[]")
    con_amts   = json.loads(row["consumable_amount"] or "[]")
    comments   = json.loads(row["comment"]           or "[]")
    tags       = json.loads(row["tag"]               or "[]")

    items = []
    for ref in item_ids:
        if ref.startswith("K:"):
            obj = get_kit_by_id(int(ref[2:]))
        else:
            obj = get_gear_by_id(int(ref[2:]))
        if obj:
            items.append(obj)

    consumables = [c for cid in con_ids if (c := _load_consumable_as_gear(cid))]

    return Trip(
        id_trip                    = row["id_trip"],
        name                       = row["name"],
        description                = row["description"],
        comments                   = comments,
        tags                       = tags,
        trip_month                 = row["trip_month"],
        duration                   = row["duration"],
        max_altitude               = row["max_altitude"],
        no_people                  = row["no_people"],
        items                      = items,
        item_amounts               = amounts,
        gear_mass_correction       = row["gear_mass_correction"] or 0,
        consumables                = consumables,
        consumable_amounts         = con_amts,
        consumable_mass_correction = row["consumable_mass_correction"] or 0,
    )


def get_all_trips() -> list[Trip]:
    """Fetch all trips ordered by name."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id_trip FROM Trip ORDER BY name")
        ids = [row["id_trip"] for row in cursor.fetchall()]
    return [t for trip_id in ids if (t := get_trip_by_id(trip_id))]

def delete_trip(trip_id: int):
    """Delete a trip and its comments."""
    from app.data.db.user_db import delete_comments_by_parent_id
    delete_comments_by_parent_id(trip_id)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM Trip WHERE id_trip = ?", (trip_id,))
    conn.commit()
    conn.close()
