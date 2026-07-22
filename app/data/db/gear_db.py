import sqlite3
from pathlib import Path
from datetime import date
from datetime import datetime

from app.core.gear_item import Gear
from app.data.db.program_db import get_brand_by_id

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
        INSERT INTO Gear (name, variant, brand_id, size, mass_pcs, price_cents, amount, color, category_id, description, prod_date, checked, lifespan, kit_only)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        gear.lifespan,
        gear.kit_only
    ))

    gear_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return gear_id


def update_gear(gear: Gear):
    """Update all fields of an existing gear item."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        UPDATE Gear SET
            name=?, variant=?, brand_id=?, size=?, mass_pcs=?, price_cents=?,
            amount=?, color=?, category_id=?, description=?, prod_date=?,
            checked=?, last_checked=?, lifespan=?, kit_only=?
        WHERE id_gear=?
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
        gear.kit_only,
        gear.id_gear,
    ))
    conn.commit()
    conn.close()

def _convert_prod_date(date_str: str):
    """Convert prod_date string to date object, return None if invalid."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def delete_gear(gear_id: int):
    """Delete a gear item and its comments."""
    from app.data.db.user_db import delete_comments_by_parent_id
    delete_comments_by_parent_id(gear_id)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM Gear WHERE id_gear = ?", (gear_id,))
    conn.commit()
    conn.close()


def get_all_gear() -> list[Gear]:
    """Fetch all gear from the database, ordered by name."""
    import sqlite3
    from pathlib import Path
    
    # Update this to your actual DB_PATH
    DB_PATH = Path("app/data/user_db.sqlite")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT * FROM Gear ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    
    gear_list = []
    for row in rows:
        gear = Gear(
            id_gear=row["id_gear"],
            name=row["name"],
            variant=row["variant"],
            brand_id=row["brand_id"],
            size=row["size"],
            mass_pcs=row["mass_pcs"],
            price=row["price_cents"] / 100 if row["price_cents"] else None,  # Convert cents to euros
            amount=row["amount"],
            color=row["color"],
            category_id=row["category_id"],
            comments=None,  # TODO: parse from JSON if stored as string
            description=row["description"],
            prod_date=_convert_prod_date(row["prod_date"]),
            checked=bool(row["checked"]),
            last_checked=row["last_checked"],
            lifespan=row["lifespan"],
            kit_only=bool(row["kit_only"])
        )
        gear_list.append(gear)
    
    return gear_list


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

        brand = None
        if row["brand_id"] is not None:
            brand = get_brand_by_id(row["brand_id"])

        # Create Gear instance with proper conversions
        gear = Gear(
            id_gear=row["id_gear"],
            name=row["name"],
            variant=row["variant"],
            brand_id=row["brand_id"],
            size=row["size"],
            mass_pcs=row["mass_pcs"],
            price=row["price_cents"] / 100 if row["price_cents"] else None,
            amount=row["amount"],
            color=row["color"],
            category_id=row["category_id"],
            description=row["description"],
            prod_date=_convert_prod_date(row["prod_date"]),
            checked=row["checked"],
            last_checked=row["last_checked"],
            lifespan=row["lifespan"],
            kit_only=bool(row["kit_only"])
        )

        return gear


def get_gear_by_filter(**kwargs):
    """
    Dynamically query gear with optional filters.
    
    Flexible gear query with dynamic filters.
    
    Supported filters: checked, brand_id, category_id, mass_above, amount_above
    Returns:
        List of gear records matching filters

    Use:
        unchecked_heavy = get_gear_by_filter(checked=0, mass_above=500)
    """

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    conditions = []
    params = []

    # Map kwargs to SQL conditions
    filter_mapping = {
        "checked": ("checked = ?", lambda v: v),
        "brand_id": ("brand_id = ?", lambda v: v),
        "category_id": ("category_id = ?", lambda v: v),
        "mass_above": ("mass_pcs > ?", lambda v: v),
        "amount_above": ("amount > ?", lambda v: v),
    }

    for key, value in kwargs.items():
        if key in filter_mapping and value is not None:
            condition, transform = filter_mapping[key]
            conditions.append(condition)
            params.append(transform(value))

    # Build query
    query = "SELECT * FROM Gear"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY name"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    gear_list = []
    for row in rows:
        gear = Gear(
            id_gear=row["id_gear"],
            name=row["name"],
            variant=row["variant"],
            brand_id=row["brand_id"],
            size=row["size"],
            mass_pcs=row["mass_pcs"],
            price=row["price_cents"] / 100 if row["price_cents"] else None,  # Convert cents to euros
            amount=row["amount"],
            color=row["color"],
            category_id=row["category_id"],
            comments=None,  # TODO: parse from JSON if stored as string
            description=row["description"],
            prod_date=_convert_prod_date(row["prod_date"]),
            checked=bool(row["checked"]),
            last_checked=row["last_checked"],
            lifespan=row["lifespan"],
            kit_only=bool(row["kit_only"])
        )
        gear_list.append(gear)
    
    return gear_list


