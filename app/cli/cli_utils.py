from app.lang import lang


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


def print_table(
    items: list[object],
    columns: list[str],
    labels: list[str] | None = None,
    col_w: int = 16,
):
    """
    Print a simple non-paged table.

    columns: list of attribute names to display
    labels: optional list of column headers; defaults to column names
    """
    if labels is None:
        labels = columns

    header = "  " + "".join(f"{label:<{col_w}}" for label in labels)
    print(header)
    print("  " + "-" * (len(header) - 2))

    for item in items:
        row = "  " + "".join(
            f"{str(getattr(item, col, '—')):<{col_w}}"
            for col in columns
        )
        print(row)

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


def paged_list(
    items: list[dict],
    columns: dict[str, str],
    default_cols: list[str],
    on_select,
    page_size: int = 10,
    title_key: str = "cli_utils.title.list",
    empty_key: str = "cli_utils.error.empty",
):
    """
    Generic paginated list with selectable columns.

    items:        list of dicts to display
    columns:      all available columns as {field_key: translation_key}
    default_cols: which columns to show initially
    on_select:    callable(item: dict) called when user picks a row
    page_size:    rows per page
    title_key:    translation key for the list title
    empty_key:    translation key shown when items is empty
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
                f"{str(getattr(item, c, None) or '—'):<{col_w}}" for c in active_cols
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

