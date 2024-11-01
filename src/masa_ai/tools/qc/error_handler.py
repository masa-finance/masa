"""
Error Handler module for the MASA project.

This module provides the ErrorHandler class, which is responsible for
handling errors and exceptions in the MASA system.

The ErrorHandler class provides decorators for handling errors and retrying
failed operations based on configuration settings.

Attributes:
    qc_manager (tools.qc.qc_manager.QCManager): Quality control manager for logging and error handling.
"""

import functools
from .exceptions import MASAException, APIException


class ErrorHandler:
    """
    Class for handling errors and exceptions in the MASA system.

    This class provides decorators for handling errors and retrying failed
    operations based on configuration settings.

    Attributes:
        qc_manager (tools.qc.qc_manager.QCManager): Quality control manager for logging and error handling.
    """

    def __init__(self, qc_manager):
        """
        Initialize the ErrorHandler.

        Args:
            qc_manager (tools.qc.qc_manager.QCManager): Quality control manager for logging and error handling.
        """
        self.qc_manager = qc_manager

    def handle_error(self, custom_handlers=None):
        """
        Decorator for handling errors in a function.

        Args:
            custom_handlers (dict, optional): Dictionary of custom error handlers for specific exception types.

        Returns:
            function: Decorated function.
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if custom_handlers and type(e) in custom_handlers:
                        return custom_handlers[type(e)](e)
                    return self._default_error_handler(e, func.__qualname__)
            return wrapper
        return decorator

    def _default_error_handler(self, e, func_name):
        """
        Default error handler for exceptions.

        Args:
            e (Exception): The exception object.
            func_name (str): Name of the function where the exception occurred.

        Raises:
            Exception: The original exception after logging the error.
        """
        if isinstance(e, MASAException):
            self.qc_manager.log_error(
                f"{type(e).__name__} in {func_name}: {str(e)}",
                error_info=e
            )
        else:
            self.qc_manager.log_error(
                f"Unexpected error in {func_name}: {str(e)}",
                error_info=e
            )
        raise

    def handle_error_with_retry(self, config_key):
        """
        Decorator for handling errors and retrying failed operations based on configuration settings.

        Args:
            config_key (str): Key in the configuration for the retry settings.

        Returns:
            function: Decorated function.
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return self.qc_manager.execute_with_retry(func, config_key, *args, **kwargs)
                except Exception as e:
                    self.qc_manager.log_error(
                        f"Function {func.__qualname__} failed after retries. Error: {str(e)}",
                        context="ErrorHandler.handle_error_with_retry"
                    )
                    raise
            return wrapper
        return decorator