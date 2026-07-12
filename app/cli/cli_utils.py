from app.lang import lang
from typing import TypeVar, Generic, Any
from app.core.utils.db_utils import fuzzy_search


# ==============================
# Display / formatting helpers
# ==============================

def print_header(title: str, width: int = 40):
    """Print a section header with divider."""
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width)


def print_divider(width: int = 40):
    """Print a simple divider line."""
    print("-" * width)


def print_table(items: list, columns: list[str], labels: list[str] | None = None, col_w: int = 16):
    """
    Print a simple non-paged table from a list of objects.
    columns: list of attribute names to display
    labels:  optional list of column headers; defaults to column names
    """
    if labels is None:
        labels = columns

    header = "  " + "".join(f"{lbl:<{col_w}}" for lbl in labels)
    print(header)
    print("  " + "-" * (len(header) - 2))
    
    for item in items:
        row = "  " + "".join(
            f"{str(_get_display_value(item, c) or '—'):<{col_w}}" for c in columns
        )
        print(row)


def _get_display_value(item, attr: str):
    """
    Get a value from an object.
    Handles nested attributes like "brand.name".
    """
    try:
        if "." in attr:
            parts = attr.split(".")
            value = item
            for part in parts:
                value = getattr(value, part, None)
                if value is None:
                    return None
            return value
        
        return getattr(item, attr, None)
    except AttributeError:
        return None

def fuzzy_pick(entity: str, db_name: str, columns: list[str], labels: list[str]) -> dict | None:
    """Fuzzy search an entity and return the chosen row as dict, or None."""
    term = input(f"Search {entity} (fuzzy): ").strip()
    if not term:
        return None
 
    results = fuzzy_search(
        table          = entity,
        search_columns = "name",
        search_term    = term,
        return_columns = columns,
        sort_by        = "name",
        db_name        = db_name,
    ) or []
 
    if not results:
        print(lang.t("delete_functions.error.not_found"))
        return None
 
    # Convert dicts to objects with attributes for print_table
    class SearchResult:
        def __init__(self, idx, **kwargs):
            self._idx = idx
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    numbered = [SearchResult(i + 1, **r) for i, r in enumerate(results)]
    print_table(
        items   = numbered,
        columns = ["_idx"] + columns,
        labels  = ["#"] + labels,
    )
 
    raw = input(lang.t("menu.cli.prompt") + " ").strip()
    if not raw.isdigit() or not (0 <= int(raw) - 1 < len(results)):
        print(lang.t("delete_functions.error.invalid_choice"))
        return None
 
    return results[int(raw) - 1]


def list_pick(items: list[tuple], columns: list[str], labels: list[str]) -> dict | None:
    """Show a simple list and let user pick by number."""
    if not items:
        print(lang.t("delete_functions.error.not_found"))
        return None
 
    rows = [dict(zip(columns, row)) for row in items]
    
    # Convert dicts to objects with attributes for print_table
    class ListResult:
        def __init__(self, idx, **kwargs):
            self._idx = idx
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    numbered = [ListResult(i + 1, **r) for i, r in enumerate(rows)]
    print_table(
        items   = numbered,
        columns = ["_idx"] + columns,
        labels  = ["#"] + labels,
    )
 
    raw = input(lang.t("menu.cli.prompt") + " ").strip()
    if not raw.isdigit() or not (0 <= int(raw) - 1 < len(rows)):
        print(lang.t("delete_functions.error.invalid_choice"))
        return None
 
    return rows[int(raw) - 1]

# ==============================
# Paged list
# ==============================

def pick_columns(columns: dict[str, str], current: list[str]) -> list[str]:
    """
    Interactively toggle which columns are visible.
    columns: {field_key: translation_key}
    current: currently active column keys
    """
    selected = list(current)
    while True:
        print(f"\n{lang.t('cli_utils.nav.toggle_hint')}")
        for i, (key, t_key) in enumerate(columns.items(), 1):
            marker = "*" if key in selected else " "
            print(f"  {i}: [{marker}] {lang.t(t_key)}")
        print(f"  {lang.t('cli_utils.nav.confirm')}")

        choice = input(lang.t("cli_utils.cli.toggle")).strip().upper()
        if choice == "C":
            return selected if selected else list(current)
        if choice.isdigit():
            idx = int(choice) - 1
            keys = list(columns.keys())
            if 0 <= idx < len(keys):
                key = keys[idx]
                if key in selected:
                    selected.remove(key)
                else:
                    selected.append(key)
            else:
                print(lang.t("cli_utils.error.invalid_selection"))
        else:
            print(lang.t("cli_utils.error.invalid_selection"))


T = TypeVar('T')  # Generic type variable

def paged_list(
    items: list[Any],  # list of objects (Gear, Brand, Trip, Kit, Category, etc.)
    columns: dict[str, str],  # {attribute_name: translation_key}
    default_cols: list[str],
    on_select,  # callable(item: T) called when user picks a row
    page_size: int = 10,
    title_key: str = "cli_utils.title.list",
    empty_key: str = "cli_utils.error.empty",
):
    """
    Generic paginated list with selectable columns.

    items:        list of objects (Gear, Brand, Trip, Kit, Category, Consumable, etc.)
    columns:      {attribute_name: translation_key} — maps object attributes to labels
    default_cols: which columns to show initially
    on_select:    callable(item) called when user picks a row
    page_size:    rows per page
    title_key:    translation key for the list title
    empty_key:    translation key shown when items is empty

    Example usage:
        paged_list(
            items=[gear1, gear2, gear3],
            columns={"name": "gear.fields.name", "variant": "gear.fields.variant"},
            default_cols=["name", "variant"],
            on_select=lambda g: display_full_gear(g),
        )
    """
    if not items:
        print(lang.t(empty_key))
        return

    active_cols = list(default_cols)
    total = len(items)
    page = 0

    while True:
        start = page * page_size
        end   = min(start + page_size, total)
        page_items = items[start:end]
        total_pages = (total - 1) // page_size + 1

        print(lang.t(title_key))

        col_w  = max(12, 60 // len(active_cols))
        labels = [lang.t(columns[c]) for c in active_cols]
        header = f"  {'#':<4}" + "".join(f"{lbl:<{col_w}}" for lbl in labels)
        print(header)
        print("  " + "-" * (len(header) - 2))

        for i, item in enumerate(page_items, 1):
            row = f"  {i:<4}" + "".join(
                f"{str(_get_display_value(item, c) or '—'):<{col_w}}" for c in active_cols
            )
            print(row)

        print(f"\n  {lang.t('cli_utils.msg.page_info', current=page+1, total=total_pages, count=total)}")
        print(f"  {lang.t('cli_utils.nav.hint')}")

        choice = input(lang.t("cli_utils.cli.select")).strip().upper()

        if choice == "N":
            if end < total:
                page += 1
            else:
                print(lang.t("cli_utils.msg.last_page"))
        elif choice == "P":
            if page > 0:
                page -= 1
            else:
                print(lang.t("cli_utils.msg.first_page"))
        elif choice == "C":
            active_cols = pick_columns(columns, active_cols)
        elif choice == "B":
            return
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(page_items):
                on_select(page_items[idx])
            else:
                print(lang.t("cli_utils.error.invalid_selection"))
        else:
            print(lang.t("cli_utils.error.invalid_selection"))


def _get_display_value(item: Any, attr: str) -> str:
    """
    Safely get an attribute from an object, handling nested attributes.
    Supports both direct attributes and properties.

    Examples:
        _get_display_value(gear, "name") → gear.name
        _get_display_value(gear, "brand.name") → gear.brand.name
        _get_display_value(trip, "trip_month") → trip.trip_month (or formatted)
    """
    try:
        # Handle nested attributes like "brand.name"
        if "." in attr:
            parts = attr.split(".")
            value = item
            for part in parts:
                value = getattr(value, part, None)
                if value is None:
                    return None
            return value

        # Simple attribute
        value = getattr(item, attr, None)

        # Special handling for certain types
        if attr == "trip_month" and value is not None:
            from app.cli.trip_functions import _month_name
            return _month_name(value)

        return value
    except (AttributeError, TypeError):
        return None


# ==============================
# Edit helpers
# ==============================

def show_diff(changes: dict):
    """Print only the changed fields."""
    if not changes:
        print(lang.t("edit_functions.title.no_changes"))
        return
    print(lang.t("edit_functions.title.changes"))
    for field, (old, new) in changes.items():
        print(f"  {lang.t(field)}: '{old}'  →  '{new}'")

def prompt_field(label: str, current, validator=None, allow_empty=True):
    """Show current value, prompt for new one."""
    raw = input(f"  {label} [{current}]: ").strip()
    if not raw:
        return current
    if validator:
        cleaned = validator(raw)
        if cleaned is None:
            print(lang.t("edit_functions.error.invalid_choice"))
            return current
        return cleaned
    return raw


# ==============================
# Input helpers
# ==============================
def confirm(prompt_key: str, **kwargs) -> bool:
    """Ask a yes/no confirmation. Returns True for Y, False for N."""
    while True:
        choice = input(lang.t(prompt_key, **kwargs)).strip().upper()
        if choice == "Y":
            return True
        if choice == "N":
            return False
        print(lang.t("cli_utils.error.invalid_selection"))

