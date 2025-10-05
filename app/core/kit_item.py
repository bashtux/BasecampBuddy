from __future__ import annotations
from typing import List, Optional
from app.core.gear_item import Gear


class Kit:
    """
    Represents a collection of gear items.
    """

    def __init__(
        self,
        id_kit: int,
        name: str,
        description: Optional[str] = None,
        comments: Optional[List[int]] = None,
        gear_list: Optional[List[Gear]] = None,
        mass_correction: int = 0,
        gear_amount: Optional[List[int]] = None,
    ):
        self.id_kit = id_kit
        self.name = name
        self.description = description
        self.comments = comments or []
        self.gear_list = gear_list or []
        self.mass_correction = mass_correction
        self.gear_amount = gear_amount or [1 for _ in self.gear_list]

        # Sanity check: gear_list and gear_amount must match in length
        if len(self.gear_list) != len(self.gear_amount):
            raise ValueError("gear_list and gear_amount must have the same length")

    # -----------------------------
    # Core behavior methods
    # -----------------------------

    def total_mass(self) -> float:
        """
        Returns the total mass of the kit.

        Each gear's `mass_pcs` is multiplied by its corresponding
        quantity from `gear_amount`, then summed up and adjusted
        by `mass_correction`.

        If any gear has no mass defined, it is treated as 0.
        """
        total = 0.0
        for gear, amount in zip(self.gear_list, self.gear_amount):
            gear_mass = gear.mass_pcs or 0
            total += gear_mass * amount

        total += self.mass_correction
        return total

    # -----------------------------
    # Utility methods
    # -----------------------------

    def add_gear(self, gear: Gear, amount: int = 1):
        """Add a gear item to the kit."""
        self.gear_list.append(gear)
        self.gear_amount.append(amount)

    def remove_gear(self, gear_id: int):
        """Remove a gear item from the kit by its ID."""
        for i, gear in enumerate(self.gear_list):
            if gear.id_gear == gear_id:
                del self.gear_list[i]
                del self.gear_amount[i]
                return True
        return False

    def __repr__(self) -> str:
        return (
            f"<Kit id={self.id_kit}, name={self.name}, "
            f"items={len(self.gear_list)}, total_mass={self.total_mass()}g>"
        )

