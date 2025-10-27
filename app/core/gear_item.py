from __future__ import annotations
from datetime import date, timedelta
from typing import Optional, List


class Gear:
    """
    Represents a single gear item in the system.
    """

    def __init__(
        self,
        name: str,
        variant: str,
        brand_id: Optional[int] = None,
        size: Optional[str] = None,
        mass_pcs: Optional[int] = None,
        price: Optional[float] = None,
        amount: int = 1,
        color: Optional[str] = None,
        category_id: Optional[int] = None,
        comments: Optional[List[int]] = None,
        description: Optional[str] = None,
        prod_date: Optional[date] = None,
        checked: bool = False,
        last_checked: Optional[date] = None,
        lifespan: Optional[int] = None,
        kit_only: bool = False,
        id_gear: int | None = None,
    ):
        self.id_gear = id_gear
        self.name = name
        self.variant = variant
        self.brand_id = brand_id
        self.size = size
        self.mass_pcs = mass_pcs
        self.price = price
        self.amount = amount
        self.color = color
        self.category_id = category_id
        self.comments = comments or []
        self.description = description
        self.prod_date = prod_date
        self.checked = checked
        self.last_checked = last_checked
        self.lifespan = lifespan
        self.kit_only = kit_only

    # -----------------------------
    # Core behavior methods
    # -----------------------------

    def is_expired(self) -> bool:
        """
        Return True if the gear is expired based on prod_date + lifespan.
        If lifespan is 0 or None, it is considered 'never expires'.
        """
        if not self.prod_date or not self.lifespan or self.lifespan == 0:
            return False

        expiry_date = self.prod_date + timedelta(days=self.lifespan * 365)
        return date.today() > expiry_date

    def check(self):
        """
        Mark the gear as checked today.
        """
        self.checked = True
        self.last_checked = date.today()


    # -----------------------------
    # Utility and representation
    # -----------------------------

    def __repr__(self) -> str:
        return (
            f"<Gear id={self.id_gear}, name={self.name}, type={self.type}, "
            f"expired={self.is_expired()}, checked={self.checked}>"
        )

