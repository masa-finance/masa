import logging
import traceback
from typing import Any, Dict
from colorlog import ColoredFormatter

class Logger:
    """
    A singleton class for handling logging in the MASA QC system.

    This class provides methods for logging various types of messages,
    including errors, warnings, and general information. It uses colorlog
    to add color formatting to the log messages.

    Attributes:
        logger (logging.Logger): The underlying Python logger object.
    """
    _instance = None

    def __new__(cls, name: str = "MASA_Logger", level: int = logging.INFO):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize(name, level)
        return cls._instance

    def _initialize(self, name: str, level: int):
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

        # Create a color formatter with a simpler format
        formatter = ColoredFormatter(
            "%(log_color)s%(levelname)s - %(message)s",
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        ch.setFormatter(formatter)

        # Add the handler to the logger
        self.logger.addHandler(ch)

    def log_error(self, error_info: Dict[str, Any]):
        """
        Log an error message with stack trace.

        Args:
            error_info (Dict[str, Any]): A dictionary containing error information.
        
        Raises:
            TypeError: If the argument is not a dictionary.
        """
        if not isinstance(error_info, dict):
            raise TypeError("The argument 'error_info' must be a dictionary.")
        
        self.logger.error(f"Error: {error_info['type']} - {error_info['message']}")
        if 'details' in error_info:
            self.logger.error(f"Details: {error_info['details']}")
        
        # Log the stack trace
        self.logger.error("Stack trace: %s", traceback.format_exc())

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