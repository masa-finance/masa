from typing import Any, Dict, Optional
from .logging import Logger 
import functools
from requests import ReadTimeout, ConnectionError, RequestException, HTTPError

class ErrorHandler:
    """
    A singleton class for handling errors in the MASA QC system.

    This class provides methods for raising and handling various types of errors,
    as well as logging error information.

    Attributes:
        logger (Logger): An instance of the Logger class for logging errors.
    """
    _instance = None

    def __new__(cls, logger: Logger = None):
        if cls._instance is None:
            cls._instance = super(ErrorHandler, cls).__new__(cls)
            cls._instance._initialize(logger)
        return cls._instance

    def _initialize(self, logger: Logger):
        """
        Initialize the ErrorHandler with a logger.

        Args:
            logger (Logger): An instance of the Logger class for logging errors.
        """
        self.logger = logger or Logger()

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
            except HTTPError as e:
                # Log HTTPError using the Logger class
                Logger().log_error({"type": "HTTPError", "message": str(e), "status_code": e.response.status_code})
                if e.response.status_code == 504:  # Gateway Timeout
                    raise GatewayTimeoutError(str(e))
                else:
                    raise RequestError(str(e))
            except (ReadTimeout, ConnectionError, RequestException) as e:
                # Log specific request exceptions using the Logger class
                Logger().log_error({"type": type(e).__name__, "message": str(e)})
                raise RequestError(str(e))
            except Exception as e:
                # Log other exceptions using the Logger class
                Logger().log_error({"type": type(e).__name__, "message": str(e)})
                raise
        return wrapper

class GatewayTimeoutError(Exception):
    """Custom exception for gateway timeout errors."""
    pass

class RequestError(Exception):
    """Custom exception for request errors."""
    pass