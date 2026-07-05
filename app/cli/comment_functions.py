import sqlite3
from pathlib import Path
from datetime import date

from app.config_manager import ConfigManager
from app.lang import lang

from app.data import db

# -----------------------------
# Load config and language
# -----------------------------
config = ConfigManager()


def input_comment(parent_id: int):
    """
    Ask the user for a new comment and insert it into the user DB.
    """
    print(lang.t("comment_functions.title.new_comment"))
    comment = input(f"{lang.t('category_functions.cli.comment')}: ").strip()

    if comment:
        db.add_comment(comment, parent_id, date.today())
        print(lang.t('comment_functions.msg.comment_added'))
    else:
        print(lang.t('comment_functions.error.invalid_choice'))

def list_comments(parent_id: int):
    """Print all available comments of parent id"""
    comments = db.get_comments_by_parent_id(parent_id)
    if not comments:
        print(lang.t("comment_functions.error.no_comments"))
        return

    print(lang.t("comment_functions.title.list_comments"))
    for com in comments:
        print(f"{com[2]:<10}: {com[3]}")


