class Brand:
    def __init__(
        self,
        name: str,
        description: str | None = None,
        url: str | None = None,
        id_brand: int | None = None,
    ):
        self.id_brand = id_brand
        self.name = name
        self.description = description
        self.url = url

    def __repr__(self):
        return f"<Brand {self.id_brand}: {self.name}>"
