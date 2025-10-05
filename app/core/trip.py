from __future__ import annotations
from typing import List, Optional, Union
from datetime import date
from app.core.gear_item import Gear
from app.core.kit_item import Kit


class Trip:
    """
    Represents a trip with gear and consumables.
    """

    def __init__(
        self,
        id_trip: int,
        name: str,
        description: Optional[str] = None,
        comments: Optional[List[int]] = None,
        tags: Optional[List[str]] = None,
        trip_month: Optional[date] = None,
        duration: int = 0,
        max_altitude: Optional[int] = None,
        no_people: int = 1,
        items: Optional[List[Union[Gear, Kit]]] = None,  # gear and kits together
        item_amounts: Optional[List[int]] = None,        # parallel list of amounts
        gear_mass_correction: int = 0,
        consumables: Optional[List[Gear]] = None,       # use Gear for consumables too
        consumable_amounts: Optional[List[int]] = None,
        consumable_mass_correction: int = 0
    ):
        self.id_trip = id_trip
        self.name = name
        self.description = description
        self.comments = comments or []
        self.tags = tags or []
        self.trip_month = trip_month
        self.duration = duration
        self.max_altitude = max_altitude
        self.no_people = no_people

        self.items = items or []
        self.item_amounts = item_amounts or [1 for _ in self.items]
        self.gear_mass_correction = gear_mass_correction

        self.consumables = consumables or []
        self.consumable_amounts = consumable_amounts or [1 for _ in self.consumables]
        self.consumable_mass_correction = consumable_mass_correction

        # sanity checks
        if len(self.items) != len(self.item_amounts):
            raise ValueError("items and item_amounts must have the same length")
        if len(self.consumables) != len(self.consumable_amounts):
            raise ValueError("consumables and consumable_amounts must match")

    # -----------------------------
    # Mass calculations
    # -----------------------------

    def gear_mass(self) -> float:
        total = sum(
            (item.total_mass() if isinstance(item, Kit) else (item.mass_pcs or 0)) * amt
            for item, amt in zip(self.items, self.item_amounts)
        )
        total += self.gear_mass_correction
        return total

    def consumable_mass(self) -> float:
        total = sum(
            (item.mass_pcs or 0) * amt for item, amt in zip(self.consumables, self.consumable_amounts)
        )
        total += self.consumable_mass_correction
        return total

    def total_mass(self) -> float:
        return self.gear_mass() + self.consumable_mass()

    # -----------------------------
    # Value calculations
    # -----------------------------

    def total_value(self) -> float:
        total = 0.0
        for item, amt in zip(self.items, self.item_amounts):
            if isinstance(item, Gear):
                total += (item.price or 0) * amt
            elif isinstance(item, Kit):
                total += sum(
                    (g.price or 0) * a * amt for g, a in zip(item.gear_list, item.gear_amount)
                )
        return total

    # -----------------------------
    # Utilities
    # -----------------------------

    def add_item(self, item: Union[Gear, Kit], amount: int = 1):
        self.items.append(item)
        self.item_amounts.append(amount)

    def add_consumable(self, consumable: Gear, amount: int = 1):
        self.consumables.append(consumable)
        self.consumable_amounts.append(amount)

    def __repr__(self) -> str:
        return (
            f"<Trip id={self.id_trip}, name={self.name}, duration={self.duration}d, "
            f"gear_mass={self.gear_mass()}g, consumable_mass={self.consumable_mass()}g>"
        )

