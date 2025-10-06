from pathlib import Path
from app.config_manager import ConfigManager
from app.data.initializer import initialize_all
from app.cli.menu import main_menu
from app.data.initializer import initialize_all

# Load configuration
config = ConfigManager()

# Start main menu
if __name__ == "__main__":
    initialize_all()
    main_menu()

