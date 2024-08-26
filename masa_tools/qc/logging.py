import logging
import traceback
from datetime import datetime
from typing import Any, Dict
from colorlog import ColoredFormatter

class Logger:
    """
    A singleton class for handling logging in the MASA QC system.

    This class provides methods for logging various types of messages,
    including errors, warnings, and general information. It uses colorlog
    to add color formatting to the log messages.

    Attributes:
        loggers (Dict[str, logging.Logger]): Dictionary of logger instances for different contexts.
        debug_enabled (bool): Flag to enable or disable debug logging.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """
        Initialize the Logger with a dictionary to store loggers for different contexts.
        """
        self.loggers = {}
        self.default_level = logging.DEBUG
        self.default_context = "MASA_Logger"
        self.debug_enabled = True  # Set to True to enable debug logging by default

    def get_logger(self, name: str, level: int = None):
        """
        Get or create a logger for a specific context.

        Args:
            name (str): The name of the logger (context).
            level (int): The logging level (default: self.default_level).

        Returns:
            logging.Logger: The logger for the specified context.
        """
        if name not in self.loggers:
            logger = logging.getLogger(name)
            level = level or self.default_level
            logger.setLevel(level)

            # Only add a handler if the logger doesn't already have one
            if not logger.handlers:
                ch = logging.StreamHandler()
                ch.setLevel(level)

                formatter = ColoredFormatter(
                    "%(log_color)s%(levelname)s - [%(name)s] %(message)s",
                    log_colors={
                        'DEBUG': 'cyan',
                        'INFO': 'green',
                        'WARNING': 'yellow',
                        'ERROR': 'red',
                        'CRITICAL': 'red,bg_white',
                    }
                )
                ch.setFormatter(formatter)

                logger.addHandler(ch)

            # Prevent propagation to avoid duplicate logs
            logger.propagate = False

            self.loggers[name] = logger

        return self.loggers[name]

    def get_timestamp(self):
        return datetime.now().isoformat()

    def log_error(self, message, error_info=None, context=None):
        if error_info is None:
            error_info = {}
        elif not isinstance(error_info, dict):
            error_info = {'error': str(error_info)}
        
        log_entry = {
            'level': 'ERROR',
            'message': message,
            'context': context or self.default_context,
            'timestamp': self.get_timestamp(),
            'error_info': error_info
        }
        logger = self.get_logger(log_entry['context'])
        logger.error(f"{log_entry['message']} - Error Info: {log_entry['error_info']}")

    def log_warning(self, message: str, context: str = "MASA_Logger"):
        """
        Log a warning message.

        Args:
            message (str): The warning message to be logged.
            context (str): The context (logger name) for this log entry.
        """
        logger = self.get_logger(context)
        logger.warning(f"Warning: {message}")

    def log_info(self, message: str, context: str = "MASA_Logger"):
        """
        Log an informational message.

        Args:
            message (str): The informational message to be logged.
            context (str): The context (logger name) for this log entry.
        """
        logger = self.get_logger(context)
        logger.info(message)

    def log_debug(self, message: str, context: str = "MASA_Logger"):
        """
        Log a debug message.

        Args:
            message (str): The debug message to be logged.
            context (str): The context (logger name) for this log entry.
        """
        if self.debug_enabled:
            logger = self.get_logger(context)
            logger.debug(message)

    def set_debug(self, enabled: bool):
        """
        Enable or disable debug logging.

        Args:
            enabled (bool): True to enable debug logging, False to disable.
        """
        self.debug_enabled = enabled