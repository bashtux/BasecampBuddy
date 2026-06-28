from app.lang import lang

from app.data import db
from app.cli.gear_functions import input_gear, display_full_gear
from app.cli.category_functions import input_category, list_categories, edit_category
from app.cli.brand_functions import input_brand, list_brands, edit_brand
from app.cli.consumable_functions import input_consumable, edit_consumable, list_consumables
from app.cli.comment_functions import input_comment, list_comments

# ====================================================
# Print Menu function
# ====================================================
def print_menu(options: dict, title_key: str, **placeholders):
    """
    Print a menu dynamically using language labels with placeholders.
    
    - options: dict of menu key -> language key
    - title_key: language key for menu title
    - placeholders: dict of placeholder_key -> language key (automatically resolved)
    """
    # Resolve all placeholders through lang.t()
    resolved_placeholders = {k: lang.t(v) for k, v in placeholders.items()}

    # Print menu title
    print(f"\n=== {lang.t(title_key, **resolved_placeholders)} ===")

    # Print menu options
    for key, label_key in options.items():
        print(f"{key}. {lang.t(label_key, **resolved_placeholders)}")

    choice = input(f"{lang.t('menu.cli.prompt', **resolved_placeholders)} ").strip()
    return choice

# ====================================================
# Main Menu function
# ====================================================
def main_menu():
    """ Display main menu """
    # key -> label_key
    commands = {
        "1": "menu.main_menu.options.gear",
        "2": "menu.main_menu.options.kit",
        "3": "menu.main_menu.options.trips",
        "4": "menu.main_menu.options.reports",
        "5": "menu.main_menu.options.settings",
        "6": "menu.main_menu.options.debug",
        "E": "menu.general_menu.options.exit"
    }
    while True:
            choice = print_menu(commands, "menu.main_menu.title")

            match choice:
                case "E":
                    print(lang.t("menu.msg.goodbye"))
                    break
                case "1":
                    gear_menu()
                    break
                case "2":
                    kit_menu()
                    break
                case "3":
                    trips_menu()
                    break
                case "4":
                    reports_menu()
                    break
                case "5":
                    settings_menu()
                    break
                case "6":
                    debug_menu()
                    break
                case _:
                    print(lang.t("menu.error.invalid_choice"))


# ====================================================
# Gear Menu function
# ====================================================
def gear_menu():
    """ Displays gear menu """
    # key -> label_key
    commands = {
            "1": "menu.general_menu.options.create",
            "2": "menu.general_menu.options.edit",
            "3": "menu.general_menu.options.list",
            "4": "menu.gear_menu.options.category",
            "5": "menu.gear_menu.options.brand",
            "D": "menu.general_menu.options.delete",
            "B": "menu.general_menu.options.back"
            }
    while True:
        choice = print_menu(commands, "menu.gear_menu.title", misc="menu.gear_menu.misc.gear")

        match choice:
            case "1":
                input_gear()
                gear_menu()
                break
            case "3":
                display_full_gear(3)
                gear_menu()
                break
            case "4":
                list_categories()
                gear_menu()
                break
            case "5":
                list_brands(db.get_all_brands(), [0, 1, 2])
                gear_menu()
                break
            case "B":
                main_menu()
                break
            case _:
                print(lang.t("menu.error.invalid_choice"))


# ====================================================
# Kit Menu function
# ====================================================
def kit_menu():
    """ Displays kit menu """
    # key -> label_key
    commands = {
            "1": "menu.general_menu.options.create",
            "2": "menu.general_menu.options.edit",
            "3": "menu.general_menu.options.list",
            "D": "menu.general_menu.options.delete",
            "B": "menu.general_menu.options.back"
            }
    while True:
        choice = print_menu(commands, "menu.kit_menu.title", misc="menu.kit_menu.misc.kit")

        match choice:
            case "1":
                print(lang.t("menu.general_menu.options.create"))
                main_menu()
                break
            case "B":
                main_menu()
                break
            case _:
                print(lang.t("menu.error.invalid_choice"))


# ====================================================
# Trips Menu function
# ====================================================
def trips_menu():
    """ Displays trips menu """
    # key -> label_key
    commands = {
            "1": "menu.general_menu.options.create",
            "2": "menu.general_menu.options.edit",
            "3": "menu.general_menu.options.list",
            "4": "menu.trips_menu.options.tags",
            "D": "menu.general_menu.options.delete",
            "B": "menu.general_menu.options.back"
            }
    while True:
        choice = print_menu(commands, "menu.trips_menu.title", misc="menu.trips_menu.misc.trips")

        match choice:
            case "1":
                print(lang.t("menu.general_menu.options.create"))
                main_menu()
                break
            case "B":
                main_menu()
                break
            case _:
                print(lang.t("menu.error.invalid_choice"))


# ====================================================
# Reports Menu function
# ====================================================
def reports_menu():
    """ Displays reports menu """
    # key -> label_key
    commands = {
            "1": "menu.reports_menu.options.expired",
            "2": "menu.reports_menu.options.unchecked",
            "3": "menu.reports_menu.options.export",
            "B": "menu.general_menu.options.back"
            }
    while True:
        choice = print_menu(commands, "menu.reports_menu.title", misc="menu.reports_menu.misc.reports")

        match choice:
            case "1":
                print(lang.t("menu.general_menu.options.create"))
                main_menu()
                break
            case "B":
                main_menu()
                break
            case _:
                print(lang.t("menu.error.invalid_choice"))


# ====================================================
# Settings Menu function
# ====================================================
def settings_menu():
    """ Displays settings menu """
    # key -> label_key
    commands = {
            "1": "menu.settings_menu.options.create_db",
            "2": "menu.settings_menu.options.set_db",
            "3": "menu.settings_menu.options.language",
            "4": "menu.settings_menu.options.edit",
            "B": "menu.general_menu.options.back"
            }
    while True:
        choice = print_menu(commands, "menu.settings_menu.title", misc="menu.settings_menu.misc.settings")

        match choice:
            case "1":
                print(lang.t("menu.general_menu.options.create"))
                main_menu()
                break
            case "4":
                edit_base_submenu()
                break
            case "B":
                main_menu()
                break
            case _:
                print(lang.t("menu.error.invalid_choice"))


# ====================================================
# Edit Base Submenu function
# ====================================================
def edit_base_submenu():
    """ Displays Edit Base submenu """
    # key -> label_key
    commands = {
            "1": "menu.edit_base_submenu.options.addbrand",
            "2": "menu.edit_base_submenu.options.editbrand",
            "3": "menu.gear_menu.options.brand",
            "4": "menu.edit_base_submenu.options.addcategory",
            "5": "menu.edit_base_submenu.options.editcategory",
            "6": "menu.gear_menu.options.category",
            "7": "menu.edit_base_submenu.options.addconsumable",
            "8": "menu.edit_base_submenu.options.editconsumable",
            "9": "menu.edit_base_submenu.options.listconsumable",
            "B": "menu.general_menu.options.back",
            "M": "menu.main_menu.title"
            }
    while True:
        choice = print_menu(commands, "menu.settings_menu.title", misc="menu.settings_menu.misc.settings")

        match choice:
            case "1":
                input_brand()
                edit_base_submenu()
                break
            case "2":
                edit_brand()
                edit_base_submenu()
                break
            case "3":
                list_brands(get_all_brands())
                edit_base_submenu()
                break
            case "4":
                input_category()
                edit_base_submenu()
                break
            case "5":
                edit_category()
                edit_base_submenu()
                break
            case "6":
                list_categories()
                edit_base_submenu()
                break
            case "7":
                input_consumable()
                edit_base_submenu()
                break
            case "8":
                edit_consumable()
                edit_base_submenu()
                break
            case "9":
                list_consumables()
                edit_base_submenu()
                break
            case "B":
                settings_menu()
                break
            case "M":
                main_menu()
                break
            case _:
                print(lang.t("menu.error.invalid_choice"))


# ====================================================
# DEBUG menu function
# ====================================================
def debug_menu():
    """ Displays DEBUG menu """
    # key -> label_key
    commands = {
            "1": "menu.debug_menu.options.add_comment",
            "2": "menu.debug_menu.options.show_comment",
            "B": "menu.general_menu.options.back"
            }
    while True:
        choice = print_menu(commands, "menu.debug_menu.title", misc="menu.debug_menu.misc.settings")

        match choice:
            case "1":
                print(lang.t("menu.general_menu.options.add_comment"))
                parent_id = _pick_parent_id()
                if parent_id is not None:
                    input_comment(parent_id)   # already takes parent_id

            case "2":
                print(lang.t("menu.debug_menu.options.show_comment"))
                parent_id = _pick_parent_id()
                if parent_id is not None:
                    list_comments(parent_id)
            case "B":
                main_menu()
                break
            case _:
                print(lang.t("menu.error.invalid_choice"))

COMMENT_PARENTS = {
    "1": ("Gear",        "gear"),
    "2": ("Trip",        "trip"),
    "3": ("Kit",         "kit"),
    "4": ("Consumable",  "consumable"),
}

def _pick_parent_id() -> int | None:
    """Ask the user which entity type and then which ID."""
    print("\nComment on:")
    for key, (label, _) in COMMENT_PARENTS.items():
        print(f"  {key}: {label}")

    choice = input("Type: ").strip()
    if choice not in COMMENT_PARENTS:
        print(lang.t("menu.error.invalid_choice"))
        return None

    label, _ = COMMENT_PARENTS[choice]
    raw = input(f"{label} ID: ").strip()
    if not raw.isdigit():
        print(lang.t("menu.error.invalid_choice"))
        return None

    return int(raw)
