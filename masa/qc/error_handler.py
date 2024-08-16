from typing import Any, Dict, Optional
from .logging import Logger

class ErrorHandler:
    """
    A class for handling errors in the MASA QC system.

    This class provides methods for raising and handling various types of errors,
    as well as logging error information.

    Attributes:
        logger (Logger): An instance of the Logger class for logging errors.
    """

    def __init__(self, logger: Logger):
        """
        Initialize the ErrorHandler with a logger.

        Args:
            logger (Logger): An instance of the Logger class for logging errors.
        """
        self.logger = logger

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

    def handle_error(self, func):
        """
        A decorator for handling errors in functions.

        This decorator catches exceptions, logs them, and re-raises them.

        Args:
            func (callable): The function to be decorated.

        Returns:
            callable: The decorated function.
        """
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_info = {
                    "type": type(e).__name__,
                    "message": str(e),
                    "function": func.__name__,
                    "args": args,
                    "kwargs": kwargs
                }
                self.logger.log_error(error_info)
                raise
        return wrapper
