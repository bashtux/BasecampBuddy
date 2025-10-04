from app.lang import Language

# Initialize language
lang = Language("en")

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

    choice = input(f"{lang.t('prompt.choice', **resolved_placeholders)} ").strip()
    return choice

# ====================================================
# Main Menu function
# ====================================================
def main_menu():
    """ Display main menu """
    # key -> label_key
    commands = {
        "1": "main_menu.options.gear",
        "2": "main_menu.options.kit",
        "3": "main_menu.options.trips",
        "4": "main_menu.options.reports",
        "5": "main_menu.options.settings",
        "E": "general_menu.options.exit"
    }
    while True:
            choice = print_menu(commands, "main_menu.title")

            match choice:
                case "E":
                    print(lang.t("msg.goodbye"))
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
                case _:
                    print(lang.t("msg.invalid_choice"))


# ====================================================
# Gear Menu function
# ====================================================
def gear_menu():
    """ Displays gear menu """
    # key -> label_key
    commands = {
            "1": "general_menu.options.create",
            "2": "general_menu.options.edit",
            "3": "general_menu.options.list",
            "4": "gear_menu.options.category",
            "D": "general_menu.options.delete",
            "B": "general_menu.options.back"
            }
    while True:
        choice = print_menu(commands, "gear_menu.title", misc="gear_menu.misc.gear")

        match choice:
            case "1":
                print(lang.t("general_menu.options.create"))
                break
            case "B":
                main_menu()
                break
            case _:
                print(lang.t("msg.invalid_choice"))


# ====================================================
# Kit Menu function
# ====================================================
def kit_menu():
    """ Displays kit menu """
    # key -> label_key
    commands = {
            "1": "general_menu.options.create",
            "2": "general_menu.options.edit",
            "3": "general_menu.options.list",
            "D": "general_menu.options.delete",
            "B": "general_menu.options.back"
            }
    while True:
        choice = print_menu(commands, "kit_menu.title", misc="kit_menu.misc.kit")

        match choice:
            case "1":
                print(lang.t("general_menu.options.create"))
                break
            case "B":
                main_menu()
                break
            case _:
                print(lang.t("msg.invalid_choice"))


# ====================================================
# Trips Menu function
# ====================================================
def trips_menu():
    """ Displays trips menu """
    # key -> label_key
    commands = {
            "1": "general_menu.options.create",
            "2": "general_menu.options.edit",
            "3": "general_menu.options.list",
            "4": "trips_menu.options.tags",
            "D": "general_menu.options.delete",
            "B": "general_menu.options.back"
            }
    while True:
        choice = print_menu(commands, "trips_menu.title", misc="trips_menu.misc.trips")

        match choice:
            case "1":
                print(lang.t("general_menu.options.create"))
                break
            case "B":
                main_menu()
                break
            case _:
                print(lang.t("msg.invalid_choice"))


# ====================================================
# Reports Menu function
# ====================================================
def reports_menu():
    """ Displays reports menu """
    # key -> label_key
    commands = {
            "1": "reports_menu.options.expired",
            "2": "reports_menu.options.unchecked",
            "3": "reports_menu.options.export",
            "B": "general_menu.options.back"
            }
    while True:
        choice = print_menu(commands, "reports_menu.title", misc="reports_menu.misc.reports")

        match choice:
            case "1":
                print(lang.t("general_menu.options.create"))
                break
            case "B":
                main_menu()
                break
            case _:
                print(lang.t("msg.invalid_choice"))


# ====================================================
# Settings Menu function
# ====================================================
def settings_menu():
    """ Displays settings menu """
    # key -> label_key
    commands = {
            "1": "settings_menu.options.create_db",
            "2": "settings_menu.options.set_db",
            "3": "settings_menu.options.language",
            "4": "settings_menu.options.edit",
            "B": "general_menu.options.back"
            }
    while True:
        choice = print_menu(commands, "settings_menu.title", misc="settings_menu.misc.settings")

        match choice:
            case "1":
                print(lang.t("general_menu.options.create"))
                break
            case "4":
                edit_base_submenu()
                break
            case "B":
                main_menu()
                break
            case _:
                print(lang.t("msg.invalid_choice"))


# ====================================================
# Edit Base Submenu function
# ====================================================
def edit_base_submenu():
    """ Displays Edit Base submenu """
    # key -> label_key
    commands = {
            "1": "edit_base_submenu.options.addbrand",
            "2": "edit_base_submenu.options.editbrand",
            "3": "edit_base_submenu.options.addcategory",
            "4": "edit_base_submenu.options.editcategory",
            "5": "edit_base_submenu.options.addconsumable",
            "6": "edit_base_submenu.options.editconsumable",
            "B": "general_menu.options.back",
            "M": "main_menu.title"
            }
    while True:
        choice = print_menu(commands, "settings_menu.title", misc="settings_menu.misc.settings")

        match choice:
            case "1":
                print(lang.t("general_menu.options.create"))
                break
            case "B":
                settings_menu()
                break
            case "M":
                main_menu()
                break
            case _:
                print(lang.t("msg.invalid_choice"))


