# masa/masa_tools/qc/qc_manager.py

from .logging_config import setup_logger
from .error_handler import ErrorHandler

class QCManager:
    _instance = None

    def __new__(cls):
        """
        Create a new instance of QCManager if one doesn't exist,
        otherwise return the existing instance.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the QCManager instance."""
        if not hasattr(self, 'logger'):
            self.logger = setup_logger("QCManager")
            self.error_handler = ErrorHandler(self)

    def log_error(self, message, error_info=None, context=None):
        """
        Log an error message.

        :param message: The error message.
        :param error_info: Additional error information (default: None).
        :param context: The context of the error (default: None).
        """
        self.logger.error(f"{context or ''}: {message}", exc_info=error_info)

    def log_warning(self, message, context=None):
        """
        Log a warning message.

        :param message: The warning message.
        :param context: The context of the warning (default: None).
        """
        self.logger.warning(f"{context or ''}: {message}")

    def log_info(self, message, context=None):
        """
        Log an info message.

        :param message: The info message.
        :param context: The context of the info (default: None).
        """
        self.logger.info(f"{context or ''}: {message}")

    def debug(self, message, context=None):
        """
        Log a debug message.

        :param message: The debug message.
        :param context: The context of the debug message (default: None).
        """
        self.logger.debug(f"{context or ''}: {message}")