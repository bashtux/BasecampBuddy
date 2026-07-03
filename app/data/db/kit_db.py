import json
import sqlite3
from pathlib import Path

from app.config_manager import ConfigManager
from app.core.kit_item import Kit
from app.data.db.gear_db import get_gear_by_id

config = ConfigManager()

BASE_DIR = Path(__file__).resolve().parents[3]
user_db_rel = config.get("paths.user_db", "app/data/user_db.sqlite")
DB_PATH = (BASE_DIR / user_db_rel).resolve()
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def add_kit(kit: Kit) -> int:
    """Insert a new kit and return its ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Kit (name, description, comments, gear_list, mass_correction, gear_amount)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        kit.name,
        kit.description,
        json.dumps(kit.comments),
        json.dumps([g.id_gear for g in kit.gear_list]),
        kit.mass_correction,
        json.dumps(kit.gear_amount),
    ))
    kit_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return kit_id


def get_kit_by_id(kit_id: int) -> Kit | None:
    """Fetch a single kit by ID, returning a Kit instance with Gear objects."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Kit WHERE id_kit = ?", (kit_id,))
        row = cursor.fetchone()
        if row is None:
            return None

    gear_ids  = json.loads(row["gear_list"]  or "[]")
    amounts   = json.loads(row["gear_amount"] or "[]")
    comments  = json.loads(row["comments"]   or "[]")

    gear_list = []
    for gear_id in gear_ids:
        gear = get_gear_by_id(gear_id)
        if gear:
            gear_list.append(gear)

    return Kit(
        id_kit          = row["id_kit"],
        name            = row["name"],
        description     = row["description"],
        comments        = comments,
        gear_list       = gear_list,
        mass_correction = row["mass_correction"] or 0,
        gear_amount     = amounts,
    )


def get_all_kits() -> list[Kit]:
    """Fetch all kits ordered by name, returning Kit instances."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id_kit FROM Kit ORDER BY name")
        ids = [row["id_kit"] for row in cursor.fetchall()]

    return [kit for kit_id in ids if (kit := get_kit_by_id(kit_id))]
