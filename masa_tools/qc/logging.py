import logging
from typing import Any, Dict

class Logger:
    """
    A class for handling logging in the MASA QC system.

    This class provides methods for logging various types of messages,
    including errors, warnings, and general information.

    Attributes:
        logger (logging.Logger): The underlying Python logger object.
    """

    def __init__(self, name: str, level: int = logging.INFO):
        """
        Initialize the Logger with a name and logging level.

        Args:
            name (str): The name of the logger.
            level (int): The logging level (default: logging.INFO).
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Create a console handler and set its level
        ch = logging.StreamHandler()
        ch.setLevel(level)

        # Create a formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)

        # Add the handler to the logger
        self.logger.addHandler(ch)

    def log_error(self, error_info: Dict[str, Any]):
        """
        Log an error message.

        Args:
            error_info (Dict[str, Any]): A dictionary containing error information.
        """
        self.logger.error(f"Error: {error_info['type']} - {error_info['message']}")
        if 'details' in error_info:
            self.logger.error(f"Details: {error_info['details']}")

    def log_warning(self, message: str):
        """
        Log a warning message.

        Args:
            message (str): The warning message to be logged.
        """
        self.logger.warning(f"Warning: {message}")

    def log_info(self, message: str):
        """
        Log an informational message.

        Args:
            message (str): The informational message to be logged.
        """
        self.logger.info(message)

    def log_debug(self, message: str):
        """
        Log a debug message.

        Args:
            message (str): The debug message to be logged.
        """
        self.logger.debug(message)
