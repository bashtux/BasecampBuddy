from datetime import date, timedelta

class GearItem:
    """
    Represents a single piece of gear.
    """

    def __init__(self, name: str, purchase_date: date, lifespan_years: int):
        self.name = name
        self.purchase_date = purchase_date
        self.lifespan_years = lifespan_years
        self.last_check: date | None = None

    def needs_check(self) -> bool:
        """
        Returns True if the item has never been checked
        or if the last check was over a year ago.
        """
        if self.last_check is None:
            return True
        return (date.today() - self.last_check).days > 365

    def is_expired(self) -> bool:
        """
        Returns True if the gear has exceeded its lifespan.
        """
        expiry_date = self.purchase_date.replace(year=self.purchase_date.year + self.lifespan_years)
        return date.today() > expiry_date

    def check(self):
        """
        Log the current date as the last check date.
        """
        self.last_check = date.today()

    def __str__(self):
        return f"{self.name} (Purchased: {self.purchase_date}, Lifespan: {self.lifespan_years}y, Last check: {self.last_check})"

