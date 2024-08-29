# masa/masa_tools/qc/qc_manager.py

from .logging_config import setup_logger
from .error_handler import ErrorHandler
from . import retry_manager as RetryManager
from configs.config import global_settings
import traceback
import sys

class QCManager:
    _instance = None

    def __new__(cls):
        """
        Create a new instance of QCManager if one doesn't exist,
        otherwise return the existing instance.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        """Initialize the QCManager instance."""
        self.logger = setup_logger("QCManager")
        self.error_handler = ErrorHandler(self)
        self.retry_manager = RetryManager.RetryPolicy(global_settings, self)

    def log_error(self, message, error_info=None, context=None):
        """
        Log an error message.

        :param message: The error message.
        :param error_info: Additional error information (default: None).
        :param context: The context of the error (default: None).
        """
        if isinstance(error_info, Exception):
            # If error_info is an exception, extract the traceback info
            tb = traceback.extract_tb(error_info.__traceback__)
            if tb:
                filename, lineno, _, _ = tb[-1]
                context = f"{context or ''} - {filename}:{lineno}"
        elif error_info:
            # If error_info is provided but not an exception, try to get filename and lineno
            filename = getattr(error_info, 'filename', 'Unknown')
            lineno = getattr(error_info, 'lineno', 'Unknown')
            context = f"{context or ''} - {filename}:{lineno}"

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

    def log_debug(self, message, context=None):
        """
        Log a debug message.

        :param message: The debug message.
        :param context: The context of the debug message (default: None).
        """
        self.logger.debug(f"{context or ''}: {message}")

    def handle_error(self, func):
        """
        Decorator to handle errors in a function.

        :param func: The function to decorate.
        :return: The decorated function.
        """
        return self.error_handler.handle_error(func)

    def handle_error_with_retry(self, config_key):
        """
        Decorator to handle errors with retry in a function.

        :param config_key: The configuration key for retry settings.
        :return: The decorated function.
        """
        return self.error_handler.handle_error_with_retry(config_key)

    def execute_with_retry(self, func, config_key, *args, **kwargs):
        return self.retry_manager.execute_with_retry(func, config_key, *args, **kwargs)