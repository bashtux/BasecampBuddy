from __future__ import annotations
from pathlib import Path
from typing import Optional


class Brand:
    """Represents a brand/manufacturer."""
    
    # Class-level cache for brands (load once)
    _brands_cache: dict[int, Brand] | None = None
    
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
    
    @classmethod
    def load_from_db(cls, db_path: str | Path = None) -> dict[int, Brand]:
        """
        Load all brands from SQLite database and cache them.
        Returns a dict mapping id_brand -> Brand object.
        
        Args:
            db_path: Path to program_db.sqlite. If None, uses default from ConfigManager.
        """
        if cls._brands_cache is not None:
            return cls._brands_cache
        
        try:
            import sqlite3
            from app.config_manager import ConfigManager
            
            if db_path is None:
                config = ConfigManager()
                # Calculate base_dir from this file's location
                # Walk up the directory tree until we find 'app' folder
                this_file = Path(__file__).resolve()
                current = this_file.parent
                base_dir = None
                
                while current != current.parent:
                    if (current / 'app').exists():
                        base_dir = current
                        break
                    current = current.parent
                
                if base_dir is None:
                    raise FileNotFoundError("Could not find project root (looking for 'app' folder)")
                
                db_rel = config.get("paths.program_db", "app/data/program_db.sqlite")
                db_path = (base_dir / db_rel).resolve()
            
            # DEBUG print(f"[Brand] Loading brands from: {db_path}")
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.execute(
                "SELECT id_brand, name, description, url FROM Brand ORDER BY name"
            )
            
            rows = cursor.fetchall()
            # DEBUG print(f"[Brand] Loaded {len(rows)} brands from database")
            
            cls._brands_cache = {
                row[0]: cls(
                    id_brand=row[0],
                    name=row[1],
                    description=row[2],
                    url=row[3]
                )
                for row in rows
            }
            conn.close()
            return cls._brands_cache
            
        except Exception as e:
            import traceback
            # DEBUG print(f"[Brand ERROR] Could not load brands from database: {e}")
            traceback.print_exc()
            cls._brands_cache = {}
            return cls._brands_cache
    
    @classmethod
    def get_by_id(cls, brand_id: int) -> Brand | None:
        """Get a Brand object by its ID, loading from database if needed."""
        brands = cls.load_from_db()
        result = brands.get(brand_id)
        return result
    
    @classmethod
    def clear_cache(cls):
        """Clear the brand cache (useful for testing or after database updates)."""
        cls._brands_cache = None
