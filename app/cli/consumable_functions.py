import sqlite3
from pathlib import Path

from app.config_manager import ConfigManager
from app.lang import lang

from app.core.utils.validation import prompt_validated_input, is_positive_number
from app.data.program_db import add_consumable, get_all_consumables, get_consumable_by_id, update_consumable

#------------------------------
# Load config and language
#------------------------------
config = ConfigManager()

def input_consumable():
    """
    Ask the user for a new category and insert it into the prorgam DB
    """
    print(lang.t("consumable_functions.title.new_consumable"))
    name = input(f"{lang.t('consumable_functions.cli.consumable_name')}: ").strip()
    description = input(f"{lang.t('consumable_functions.cli.consumable_description')}: ").strip()
    weight = prompt_validated_input(
            prompt_key="consumable_functions.cli.consumable_weight",
            validator=is_positive_number,
            allow_empty=False,
            error_key="consumable_functions.error.no_number"
    )

    if name:
        add_consumable(name, description, weight)
        print(lang.t("consumable_functions.msg.consumable_added").format(consumable_name=name))
    else:
        print(lang.t("consumable_functions.error.no_name"))


def list_consumables():
    """Print all available consumables with weight and description."""
    consumables = get_all_consumables()
    if not consumables:
        print(lang.t("consumable_functions.error.not_found"))
        return

    print(lang.t("consumable_functions.title.list_consumables"))
    for con in consumables:
        print(f"{con[0]:<3} | {con[3]:<4}g | {con[1]} - {con[2]}")


def edit_consumable():
    """Allow user do edit a consumable (name, description, weight)."""
    print(lang.t("consumable_functions.title.edit_consumable"))
    list_consumables()

    try:
        consumable_id = int(input(lang.t("consumable_functions.cli.select_id")))
    except ValueError:
        print(lang.t("consumable_functions.error.invalid_choice"))
        return

    consumable = get_consumable_by_id(consumable_id)
    if not consumable:
        print(lang.t("consumable_functions.error.not_found"))
        return

    print(lang.t("consumable_functions.msg.current_values").format(name=consumable[1], desc=consumable[2], weight=consumable[3]))

    new_name = input(f"{(consumable[1])}\n {lang.t('consumable_functions.cli.new_name')}: ") or consumable[1]

    new_description = input(f"{(consumable[2])}\n {lang.t('consumable_functions.cli.new_description')}: ") or consumable[2]

    new_weight = (
            prompt_validated_input(
                prompt_key="consumable_functions.cli.new_weight",
                validator=is_positive_number,
                allow_empty=True,
                error_key="consumable_functions.error.no_number"
                )
    or consumable[3]
    )

    update_consumable(consumable_id, new_name, new_description, new_weight)
    print(lang.t("consumable_functions.msg.success"))
    return
