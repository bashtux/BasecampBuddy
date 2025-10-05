from pathlib import Path
from app.config_manager import ConfigManager
from app.lang import Language
from app.data.initializer import initialize_all
from app.cli.menu import main_menu

# Load configuration
config = ConfigManager(Path(__file__).parent / "app" / "config")

# Start main menu
if __name__ == "__main__":
    initialize_all()
    main_menu()

