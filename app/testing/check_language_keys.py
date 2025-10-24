import os
import re
import json
from collections import defaultdict

CODE_DIR = "app"
LANG_DIR = "app/i18n"

LANG_KEYS_PATTERN = re.compile(r'lang\.t\(["\']([\w\.\- ]+)["\']\)')

def flatten_json_keys(d, prefix="", file_map=None, file_path=""):
    """Flatten nested JSON keys, prepending the JSON file name as prefix."""
    if file_map is None:
        file_map = {}
    if isinstance(d, dict):
        for k, v in d.items():
            k_clean = k.replace(" ", "")
            full_key = f"{prefix}.{k_clean}" if prefix else k_clean
            flatten_json_keys(v, full_key, file_map, file_path)
    elif isinstance(d, list):
        for i, v in enumerate(d):
            full_key = f"{prefix}[{i}]" if prefix else str(i)
            flatten_json_keys(v, full_key, file_map, file_path)
    else:
        file_map[prefix] = file_path
    return file_map

def get_lang_file_keys(lang_dir):
    """Scan all JSON language files and return dict: {lang: {key: file_path}}."""
    lang_keys = {}
    for lang in os.listdir(lang_dir):
        lang_path = os.path.join(lang_dir, lang)
        if os.path.isdir(lang_path):
            combined = {}
            for file in os.listdir(lang_path):
                if file.endswith(".json"):
                    file_prefix = os.path.splitext(file)[0]  # filename as prefix
                    path = os.path.join(lang_path, file)
                    try:
                        with open(path, encoding="utf-8") as fh:
                            data = json.load(fh)
                            flatten_json_keys(data, prefix=file_prefix, file_map=combined, file_path=path)
                    except json.JSONDecodeError:
                        print(f"⚠️ JSON error in {path}")
            lang_keys[lang] = combined
    return lang_keys

def get_used_lang_keys():
    """Scan code files and return dict {key: {file_path: [lines]}}."""
    used = defaultdict(lambda: defaultdict(list))
    for root, _, files in os.walk(CODE_DIR):
        for f in files:
            if f.endswith((".py", ".js", ".ts")):
                path = os.path.join(root, f)
                with open(path, encoding="utf-8") as fh:
                    for lineno, line in enumerate(fh, 1):
                        for key in LANG_KEYS_PATTERN.findall(line):
                            key_clean = key.replace(" ", "")
                            used[key_clean][path].append(lineno)
    return used

def check_language_keys():
    lang_keys = get_lang_file_keys(LANG_DIR)
    used_keys = get_used_lang_keys()

    for lang, keys in lang_keys.items():
        print(f"\nChecking language: {lang}")
        all_ok = True

        # Missing keys: keys used in code but not defined in JSON
        missing = []
        for code_key, files in used_keys.items():
            if code_key not in keys:
                missing.append((code_key, files))

        if missing:
            print(f"\n❌ Missing in {lang}: {len(missing)} keys")
            for key, file_map in missing:
                for file_path, lines in file_map.items():
                    line_str = ", ".join(str(l) for l in lines)
                    print(f"{key} : {file_path} : lines {line_str}")
            all_ok = False
        else:
            print(f"\n✅ {lang}: all used keys exist!")

        if all_ok:
            print(f"\n✅ All keys exist and are used in {lang}!")

if __name__ == "__main__":
    check_language_keys()

