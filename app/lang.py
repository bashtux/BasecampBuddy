import json
from pathlib import Path
from app.config_manager import ConfigManager

class Language:
    def __init__(self, lang_code: str = "en"):
        self.lang_code = lang_code
        self.lang_dir = Path("app/i18n")
        # load selected language and fallback language (English)
        self.translations = self._load_all_files(self.lang_code)
        if self.lang_code != "en":
            self.fallback_translations = self._load_all_files("en")
        else:
            self.fallback_translations = {}

    def _load_all_files(self, lang_code: str) -> dict:
        merged = {}
        lang_path = self.lang_dir / lang_code
        if not lang_path.exists():
            raise FileNotFoundError(f"Language folder {lang_path} not found")

        for file in lang_path.glob("*.json"):
            key_prefix = file.stem  # use filename as top-level key
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

            merged[key_prefix] = data
        return merged

    def t(self, key: str, **kwargs) -> str:
        """
        Translate a key using dot notation: 'file.topkey.subkey'.
        kwargs can be used for dynamic replacements: lang.t("messages.hello", name="Joe").
        Falls back to English if key is missing in selected language.
        """
        value = self._get_from_dict(self.translations, key)
        if value is None:
            value = self._get_from_dict(self.fallback_translations, key)
            if value is None:
                return f"[MISSING: {key}]"
        if isinstance(value, str) and kwargs:
            return value.format(**kwargs)
        return value

    @staticmethod
    def _get_from_dict(d: dict, key: str):
        parts = key.split(".")
        node = d
        try:
            for part in parts:
                node = node[part]
            return node
        except (KeyError, TypeError):
            return None

# --- initialize using config ---
_config = ConfigManager()       # reads defaults + user config
user_lang = _config.get("general.language", "en")
lang = Language(user_lang)
