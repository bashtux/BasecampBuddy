import sqlite3
from pathlib import Path
from datetime import date

from app.core import Gear

from app.config_manager import ConfigManager  # assuming you have this
from app.lang import lang

# Load config once
config = ConfigManager()  # reads defaults + user config

# Determine project root
BASE_DIR = Path(__file__).resolve().parents[3]  # goes from app/data -> project root

# Path to program DB from config, fallback to default
user_db_rel = config.get("paths.user_db", "app/data/user_db.sqlite")
DB_PATH = (BASE_DIR / user_db_rel).resolve()

# Ensure parent folder exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def add_gear(gear: Gear) -> int:
    """Insert a new gear item and return its ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO gear_item (name, type, brand, size, mass_pcs, price, amount, color, category, comments, description, prod_date, checked, last_checked, lifespan, kit_only)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        gear.name,
        gear.type,
        gear.brand_id,
        gear.size,
        gear.mass_pcs,
        gear.price,
        gear.amount,
        gear.color,
        gear.category_id,
        gear.comments,
        gear.description,
        gear.prod_date.isoformat() if gear.purchase_date else None,
        gear.checked,
        gear.last_checked,
        gear.lifespan,
        gear.kit_only
    ))

    gear_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return gear_id


def get_gear_by_id(gear_id: int) -> Gear | None:
    """Fetch a gear item by ID and return a Gear object."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id_gear, name, brand_id, category_id, purchase_date, lifespan_years, notes
        FROM gear_item WHERE id_gear = ?
    """, (gear_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return Gear(
            id_gear=row[0],
            name=row[1],
            brand_id=row[2],
            category_id=row[3],
            purchase_date=date.fromisoformat(row[4]) if row[4] else None,
            lifespan_years=row[5],
            notes=row[6]
        )
    return None


def get_all_gear() -> list[Gear]:
    """Return all gear items from the DB."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id_gear, name, brand_id, category_id, purchase_date, lifespan_years, notes
        FROM gear_item ORDER BY name
    """)
    rows = cursor.fetchall()
    conn.close()

    return [
        Gear(
            id_gear=row[0],
            name=row[1],
            brand_id=row[2],
            category_id=row[3],
            purchase_date=date.fromisoformat(row[4]) if row[4] else None,
            lifespan_years=row[5],
            notes=row[6]
        )
        for row in rows
    ]
