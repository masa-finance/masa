from typing import Any, Dict, Optional
from .logging import Logger
import logging
import functools
from requests import ReadTimeout, ConnectionError, RequestException

class ErrorHandler:
    """
    A class for handling errors in the MASA QC system.

    This class provides methods for raising and handling various types of errors,
    as well as logging error information.

    Attributes:
        logger (Logger): An instance of the Logger class for logging errors.
    """

    def __init__(self, logger: None):
        """
        Initialize the ErrorHandler with a logger.

        Args:
            logger (Logger): An instance of the Logger class for logging errors.
        """
        self.logger = logger or Logger("ErrorHandler").logger

    def raise_error(self, error_type: str, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Raise and log an error with the specified type and message.

        Args:
            error_type (str): The type of error (e.g., "ValueError", "RuntimeError").
            message (str): A descriptive error message.
            details (Optional[Dict[str, Any]]): Additional details about the error.

        Raises:
            Exception: The specified error type with the given message.
        """
        error_info = {
            "type": error_type,
            "message": message,
            "details": details or {}
        }
        self.logger.log_error(error_info)
        
        # Raise the appropriate exception
        exception_class = globals().get(error_type, Exception)
        raise exception_class(message)

    @staticmethod
    def handle_error(func):
        """
        A decorator for handling errors in functions.

        This decorator catches exceptions, logs them, and re-raises them.

        Args:
            func (callable): The function to be decorated.

        Returns:
            callable: The decorated function.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (ReadTimeout, ConnectionError, RequestException) as e:
                # Log specific request exceptions using the provided logger
                if hasattr(wrapper, 'logger'):
                    wrapper.logger.error(f"A request error occurred in {func.__name__}: {e}")
                else:
                    logging.error(f"A request error occurred in {func.__name__}: {e}")
                raise
            except Exception as e:
                # Log other exceptions using the provided logger
                if hasattr(wrapper, 'logger'):
                    wrapper.logger.error(f"An error occurred in {func.__name__}: {e}")
                else:
                    logging.error(f"An error occurred in {func.__name__}: {e}")
                raise
        return wrapper