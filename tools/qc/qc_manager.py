"""
QC Manager module for the MASA project.

This module provides the QCManager class, which centralizes quality control
tasks such as logging, error handling, and retry management.
"""

from .logging_config import setup_logger
from .error_handler import ErrorHandler
from . import retry_manager as RetryManager
from configs.config import global_settings
import traceback
import inspect

class QCManager:
    """
    Quality Control Manager for the MASA project.

    This class provides centralized functionality for logging, error handling,
    and retry management. It follows a singleton pattern to ensure only one
    instance is used throughout the application.

    Attributes:
        logger: The logger instance for this QCManager.
        error_handler: An instance of ErrorHandler for managing errors.
        retry_manager: An instance of RetryPolicy for managing retries.
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.initialize()
            self._initialized = True

    def initialize(self):
        """Initialize the QCManager instance."""
        self.logger = setup_logger("QCManager")
        self.error_handler = ErrorHandler(self)
        self.retry_manager = RetryManager.RetryPolicy(global_settings, self)

    def log_error(self, message, error_info=None, context=None):
        """
        Log an error message.

        Args:
            message (str): The error message.
            error_info (Exception, optional): Additional error information.
            context (str, optional): The context of the error.
        """
        method_name = inspect.currentframe().f_back.f_code.co_name
        context = f"{context or ''} - {method_name}"

        if isinstance(error_info, Exception):
            tb = traceback.extract_tb(error_info.__traceback__)
            if tb:
                filename, lineno, _, _ = tb[-1]
                context = f"{context} - {filename}:{lineno}"
        elif error_info:
            filename = getattr(error_info, 'filename', 'Unknown')
            lineno = getattr(error_info, 'lineno', 'Unknown')
            context = f"{context} - {filename}:{lineno}"

        self.logger.error(f"{context}: {message}", exc_info=error_info)

    def log_warning(self, message, context=None):
        """
        Log a warning message.

        Args:
            message (str): The warning message.
            context (str, optional): The context of the warning.
        """
        method_name = inspect.currentframe().f_back.f_code.co_name
        context = f"{context or ''} - {method_name}"
        self.logger.warning(f"{context}: {message}")

    def log_info(self, message, context=None):
        """
        Log an info message.

        Args:
            message (str): The info message.
            context (str, optional): The context of the info.
        """
        method_name = inspect.currentframe().f_back.f_code.co_name
        context = f"{context or ''} - {method_name}"
        self.logger.info(f"{context}: {message}")

    def log_debug(self, message, context=None):
        """
        Log a debug message.

        Args:
            message (str): The debug message.
            context (str, optional): The context of the debug message.
        """
        method_name = inspect.currentframe().f_back.f_code.co_name
        context = f"{context or ''} - {method_name}"
        self.logger.debug(f"{context}: {message}")

    def handle_error(self, func):
        """
        Decorator to handle errors in a function.

        Args:
            func (callable): The function to decorate.

        Returns:
            callable: The decorated function.
        """
        return self.error_handler.handle_error(func)

    def handle_error_with_retry(self, config_key):
        """
        Decorator to handle errors with retry in a function.

        Args:
            config_key (str): The configuration key for retry settings.

        Returns:
            callable: The decorator function.
        """
        return self.error_handler.handle_error_with_retry(config_key)

    def execute_with_retry(self, func, config_key, *args, **kwargs):
        """
        Execute a function with retry logic.

        Args:
            func (callable): The function to execute.
            config_key (str): The configuration key for retry settings.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            The result of the function execution.
        """
        return self.retry_manager.execute_with_retry(func, config_key, *args, **kwargs)