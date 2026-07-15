from __future__ import annotations


class Category:
    """Represents a gear category."""
    
    def __init__(
        self,
        id_category: int,
        name: str,
        description: str | None = None,
    ):
        self.id_category = id_category
        self.name = name
        self.description = description
    
    def __repr__(self):
        return f"<Category {self.id_category}: {self.name}>"
