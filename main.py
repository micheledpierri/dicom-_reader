#!/usr/bin/env python3
"""
DICOM Reader - Main Entry Point
A comprehensive DICOM file viewer with advanced features
"""

import sys
import logging
from PyQt5.QtWidgets import QApplication

from dicom_reader.gui import MainWindow
from dicom_reader.utils import Config


def setup_logging():
    """Configure logging for the application"""
    log_file = Config.LOG_DIR / "dicom_reader.log"

    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format=Config.LOG_FORMAT,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Starting {Config.APP_NAME} v{Config.APP_VERSION}")
    logger.info(f"Log file: {log_file}")


def main():
    """Main application entry point"""
    # Setup logging
    setup_logging()

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName(Config.APP_NAME)
    app.setApplicationVersion(Config.APP_VERSION)

    # Create and show main window
    window = MainWindow()
    window.show()

    # Run application
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
