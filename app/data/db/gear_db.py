import sqlite3
from pathlib import Path
from datetime import date

from app.core.gear_item import Gear

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
        INSERT INTO Gear (name, variant, brand_id, size, mass_pcs, price_cents, amount, color, category_id, description, prod_date, checked, last_checked, lifespan, kit_only)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        gear.name,
        gear.variant,
        gear.brand_id,
        gear.size,
        gear.mass_pcs,
        gear._price_cents,
        gear.amount,
        gear.color,
        gear.category_id,
        gear.description,
        gear.prod_date.isoformat() if gear.prod_date else None,
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
    """
    Fetches a single gear item by its ID, converts types,
    and returns a Gear instance or None if not found.
    """

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM gear WHERE id_gear = ?", (gear_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        # Create Gear instance with proper conversions
        gear = Gear(
            id_gear=row["id_gear"],
            name=row["name"],
            variant=row["variant"],
            brand_id=row["brand_id"],
            size=row["size"],
            mass_pcs=row["mass_pcs"],
            _price_cents=row["price_cents"],
            amount=row["amount"],
            color=row["color"],
            category_id=row["category_id"],
            description=row["description"],
            prod_date=row["prod_date"],
            checked=row["checked"],
            last_checked=row["last_checked"],
            lifespan=row["lifespan"],
            kit_only=bool(row["kit_only"])
        )

        return gear

