
# =========================================
# Logging Configuration Utility
# =========================================
# Centralized logging setup for the application.
# Provides a global logger and a function to get module-specific loggers.
#
# Usage:
#   from app.utils.logger import logger
#   logger.info("Message")
#   my_logger = get_logger("my_module")
#   my_logger.debug("Debug message")

import logging  # Standard Python logging module
import sys
from app.config import settings

def setup_logging():
    """
    Set up the root logger for the application.
    - Sets log level based on debug mode.
    - Configures output format and console handler.
    Returns:
        logging.Logger: Configured root logger
    """
    # Create logger
    logger = logging.getLogger("engineering_tools")
    logger.setLevel(logging.INFO if not settings.debug else logging.DEBUG)

    # Remove existing handlers to avoid duplicate logs
    logger.handlers.clear()

    # Create console handler for stdout
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO if not settings.debug else logging.DEBUG)

    # Set log message format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    return logger

# Global logger instance for use throughout the app
logger = setup_logging()

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module or component.
    Args:
        name (str): Name of the module (e.g., __name__)
    Returns:
        logging.Logger: Logger with hierarchical name
    """
    return logging.getLogger(f"engineering_tools.{name}")