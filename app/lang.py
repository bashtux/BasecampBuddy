import json
from pathlib import Path
from app.config_manager import ConfigManager

class Language:
    def __init__(self, lang_code="en"):
        self.lang_code = lang_code
        self.lang_dir = Path(__file__).parent / "i18n"
        self.translations = self._load_language(lang_code)

    def _load_language(self, lang_code):
        lang_file = self.lang_dir / f"{lang_code}.json"
        if not lang_file.exists():
            print(f"⚠️ Language file '{lang_code}' not found. Falling back to English.")
            lang_file = self.lang_dir / "en.json"

        with open(lang_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def t(self, key: str, **kwargs) -> str:
        """Translate a text key using dot notation and format placeholders."""
        parts = key.split(".")
        value = self.translations
        try:
            for part in parts:
                value = value[part]
        except (KeyError, TypeError):
            return f"\033[91m{key}\033[0m"  # red text

        # If placeholders are provided, format the string
        if kwargs:
            try:
                value = value.format(**kwargs)
            except KeyError as e:
                print(f"⚠️ Missing placeholder in key '{key}': {e}")
        return value

# ------------------------
# Global instance
# ------------------------
_config = ConfigManager()
_lang_instance = Language(_config.get("language", "en"))

def get_lang():
    """Return the current global Language instance."""
    return _lang_instance

def reload_lang():
    """Reload language if config changes."""
    global _lang_instance
    new_code = _config.get("language", "en")
    _lang_instance = Language(new_code)
