import sqlite3
from pathlib import Path

from app.config_manager import ConfigManager
from app.lang import lang

from app.core.utils.validation import prompt_validated_input, is_positive_number
from app.data.program_db import add_consumable

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


