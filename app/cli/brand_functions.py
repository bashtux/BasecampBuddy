import sqlite3
import pathlib from Path
from app.config_manager import ConfigManager
from app.data.program_db import add_brand
from app.lang import lang

#--------------------------
# Load config and language
#--------------------------
config = ConfigManager()


