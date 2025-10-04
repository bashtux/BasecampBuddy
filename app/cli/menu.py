from app.lang import Language

# Initialize language
lang = Language("en")

def print_menu(options: dict, title_key: str):
    """Print a menu dynamically from options dictionary."""
    print(f"\n=== {lang.t(title_key)} ===")
    for key, label_key in options.items():
        print(f"{key}. {lang.t(label_key)}")
    choice = input(f"{lang.t('prompt.choice')} ").strip()
    return choice

def main_menu():
    # key -> label_key
    commands = {
        "1": "menu.options.list",
        "2": "menu.options.add",
        "3": "menu.options.remove",
        "0": "menu.options.exit"
    }

    while True:
        choice = print_menu(commands, "menu.title")
        if choice in commands:
            # Placeholder actions
            if choice == "0":
                print(lang.t("msg.goodbye"))
                break
            else:
                print(f"Selected: {lang.t(commands[choice])} (action placeholder)")
        else:
            print(lang.t("msg.invalid_choice"))

