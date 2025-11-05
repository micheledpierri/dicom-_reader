"""
Configuration Module
Application configuration and settings
"""

import os
from pathlib import Path


class Config:
    """Application configuration"""

    # Application info
    APP_NAME = "DICOM Reader"
    APP_VERSION = "1.0.0"

    # Paths
    HOME_DIR = Path.home()
    APP_DIR = HOME_DIR / ".dicom_reader"
    DATABASE_PATH = APP_DIR / "dicom_database.db"
    LOG_DIR = APP_DIR / "logs"

    # Ensure directories exist
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories"""
        cls.APP_DIR.mkdir(exist_ok=True)
        cls.LOG_DIR.mkdir(exist_ok=True)

    # Viewer settings
    DEFAULT_WINDOW_CENTER = 40
    DEFAULT_WINDOW_WIDTH = 400

    # Cine settings
    DEFAULT_CINE_FPS = 10
    MIN_CINE_FPS = 1
    MAX_CINE_FPS = 60

    # Database settings
    DB_ECHO = False  # Set to True for SQL debugging

    # Logging settings
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # UI settings
    MAIN_WINDOW_WIDTH = 1400
    MAIN_WINDOW_HEIGHT = 900


# Ensure directories are created on import
Config.ensure_directories()
