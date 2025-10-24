import os
import re
import json

LANG_DIR = "app/i18n"
CODE_DIR = "app"
LANG_KEYS_PATTERN = re.compile(r'lang\.t\(["\']([a-zA-Z0-9_.-]+)["\']\)')

def flatten_json_keys(d, prefix=""):
    keys = set()
    for k, v in d.items():
        full_key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            keys |= flatten_json_keys(v, full_key)
        else:
            keys.add(full_key)
    return keys

def get_used_lang_keys():
    used = set()
    for root, _, files in os.walk(CODE_DIR):
        for f in files:
            if f.endswith(".py"):
                with open(os.path.join(root, f), encoding="utf-8") as fh:
                    content = fh.read()
                    used |= set(LANG_KEYS_PATTERN.findall(content))
    return used

def get_lang_file_keys(lang_dir):
    lang_keys = {}
    for lang in os.listdir(lang_dir):
        lang_path = os.path.join(lang_dir, lang)
        if os.path.isdir(lang_path):
            combined = set()
            for file in os.listdir(lang_path):
                if file.endswith(".json"):
                    path = os.path.join(lang_path, file)
                    try:
                        data = json.load(open(path, encoding="utf-8"))
                        combined |= flatten_json_keys(data)
                    except json.JSONDecodeError:
                        print(f"⚠️ JSON error in {path}")
            lang_keys[lang] = combined
    return lang_keys

def check_language_keys():
    used_keys = get_used_lang_keys()
    lang_keys = get_lang_file_keys(LANG_DIR)

    print(f"Found {len(used_keys)} language keys used in code.\n")

    all_ok = True
    for lang, keys in lang_keys.items():
        missing = sorted(used_keys - keys)
        if missing:
            print(f"❌ Missing in {lang}: {len(missing)} keys")
            for k in missing:
                print(f"   - {k}")
            all_ok = False
        else:
            print(f"✅ {lang}: all keys exist!")

    if all_ok:
        print("\n✅ All keys exist in all language files!")
    else:
        print("\n⚠️ Some keys are missing!")

if __name__ == "__main__":
    check_language_keys()

