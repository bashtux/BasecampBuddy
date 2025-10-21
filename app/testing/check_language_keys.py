# app/testing/check_language_keys.py

import os
import re
import json

# -------- CONFIG --------
APP_SRC = "../"  # relative to the testing folder
LANG_FOLDER = "../i18n"  # path to your language files
LANG_FILES = [f for f in os.listdir(LANG_FOLDER) if f.endswith(".json")]

# -------- FUNCTIONS --------

def get_used_keys(src_path):
    """Scan Python files and extract all lang.t() keys."""
    keys_used = set()
    pattern = re.compile(r'lang\.t\(["\']([\w\.]+)["\']\)')
    for root, dirs, files in os.walk(src_path):
        for file in files:
            if file.endswith(".py"):
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    text = f.read()
                    keys_used.update(pattern.findall(text))
    return keys_used


def flatten_lang_dict(d, parent=""):
    """Flatten nested language dict into dot notation keys."""
    items = []
    for k, v in d.items():
        new_key = f"{parent}.{k}" if parent else k
        if isinstance(v, dict):
            items.extend(flatten_lang_dict(v, new_key))
        else:
            items.append(new_key)
    return items


def load_language_files(lang_folder, lang_files):
    """Load all language files and return a dict: {filename: set(keys)}"""
    lang_data = {}
    for lang_file in lang_files:
        with open(os.path.join(lang_folder, lang_file), "r", encoding="utf-8") as f:
            data = json.load(f)
        lang_data[lang_file] = set(flatten_lang_dict(data))
    return lang_data


def check_language_file(lang_keys, used_keys):
    """Check missing and unused keys for a single language file."""
    missing = used_keys - lang_keys
    unused = lang_keys - used_keys
    return missing, unused


def cross_language_check(all_lang_keys):
    """Check for keys present in some languages but missing in others."""
    all_keys = set().union(*all_lang_keys.values())
    cross_missing = {}
    for key in all_keys:
        missing_in = [lang for lang, keys in all_lang_keys.items() if key not in keys]
        if missing_in:
            cross_missing[key] = missing_in
    return cross_missing


# -------- MAIN --------

if __name__ == "__main__":
    used_keys = get_used_keys(APP_SRC)
    print(f"Found {len(used_keys)} language keys used in code.\n")

    all_lang_keys = load_language_files(LANG_FOLDER, LANG_FILES)

    # Per-language check
    for lang_file, keys in all_lang_keys.items():
        missing, unused = check_language_file(keys, used_keys)
        print(f"--- {lang_file} ---")
        if missing:
            print(f"Missing keys ({len(missing)}):")
            for k in sorted(missing):
                print(f"  {k}")
        else:
            print("No missing keys!")

        if unused:
            print(f"Unused keys ({len(unused)}):")
            for k in sorted(unused):
                print(f"  {k}")
        else:
            print("No unused keys!")
        print()

    # Cross-language consistency check
    cross_missing = cross_language_check(all_lang_keys)
    if cross_missing:
        print("=== Cross-language missing keys ===")
        for key, langs in sorted(cross_missing.items()):
            print(f"{key} missing in: {', '.join(langs)}")
    else:
        print("All keys exist in all language files!")

