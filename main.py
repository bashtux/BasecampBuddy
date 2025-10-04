from pathlib import Path
from app.config_manager import ConfigManager
from app.lang import Language
from app.cli.menu import main_menu

# Load configuration
config = ConfigManager(Path(__file__).parent / "app" / "config")

# Initialize language
#lang = Language(config.get("language", "en"))

# Start main menu
if __name__ == "__main__":
    main_menu()

