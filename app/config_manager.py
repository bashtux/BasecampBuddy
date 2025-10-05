import json
from pathlib import Path

class ConfigManager:
    def __init__(self, config_dir=None):
        if config_dir is None:
            config_dir = "app/config"  # default path
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.json"
        self.default_file = self.config_dir / "defaults.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()

        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load defaults and merge with user config."""
        with open(self.default_file, "r", encoding="utf-8") as f:
            config = json.load(f)

        if self.config_file.exists():
            with open(self.config_file, "r", encoding="utf-8") as f:
                user_config = json.load(f)
                config.update(user_config)

        return config

    def save(self):
        """Write current settings to file."""
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save()

