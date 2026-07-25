import sqlite3
from pathlib import Path
from fuzzywuzzy import fuzz

from app.config_manager import ConfigManager
from app.lang import lang

# Load config once
config = ConfigManager()

#·Determine·project·root
BASE_DIR = Path(__file__).resolve().parents[3] #·goes·from·app/data·->·project·root

#·Path·to·program·DB·from·config,·fallback·to·deifault
#program_db_rel·=·config.get("paths.program_db",·"app/data/program_db.sqlite")
#DB_PATH·=·(BASE_DIR·/·program_db_rel).resolve()

def fuzzy_search(
    table: str,
    search_columns: str | list[str],
    search_term: str,
    return_columns: list[str] | None = None,
    limit: int | None = 10,
    sort_by: str | list[str] | None = None,
    sort_order: str = "ASC",
    min_similarity: int = 60,
    db_name: str = "program_db",
    object_class = None,  # NEW: Pass the class to instantiate
) -> list:
    """
    Returns a list of objects (Brand, Gear, etc.) instead of dicts.
    
    Args:
        object_class: The class to instantiate (Brand, Gear, etc.)
                     If None, returns dicts (backward compat)
    """

    # Determine DB path via config manager
    db_path_str = config.get(f"paths.{db_name}", f"app/data/{db_name}.sqlite")
    db_path = Path(db_path_str)

    # Normalize arguments
    if isinstance(search_columns, str):
        search_columns = [search_columns]
    if isinstance(sort_by, str):
        sort_by = [sort_by]

    # SQL for the table
    columns_sql = ", ".join(return_columns) if return_columns else "*"
    query = f"SELECT {columns_sql} FROM {table}"

    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            results = []

            for row in rows:
                row_dict = dict(row)
                best_score = 0

                for col in search_columns:
                    value = str(row_dict.get(col, ""))
                    score = fuzz.partial_ratio(search_term.lower(), value.lower())
                    best_score = max(best_score, score)

                if best_score >= min_similarity:
                    row_dict["_similarity"] = best_score
                    results.append(row_dict)

            # Sort by requested column(s), then similarity
            if sort_by:
                for col in reversed(sort_by):
                    results.sort(
                        key=lambda x: x.get(col, ""),
                        reverse=(sort_order.upper() == "DESC"),
                    )

            results.sort(key=lambda x: x["_similarity"], reverse=True)

            if limit:
                results = results[:limit]

            if object_class is None:
                    return results  # Return dicts as before
        
        # Convert dicts to objects
        return [object_class(**{k: v for k, v in row.items() if k != "_similarity"}) for row in results]

    except sqlite3.Error as e:
        print(lang.t("db_utils.error.query_failed"), e)
        return []
