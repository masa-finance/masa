import functools
import traceback
import time
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout, ReadTimeout
from .logging import Logger
from tqdm import tqdm

class RequestError(Exception):
    """
    Base class for request-related errors.

    This class serves as a base for more specific request error classes.
    """
    pass

class RateLimitError(RequestError):
    """
    Exception raised when the rate limit is exceeded.

    Attributes:
        retry_after (int): The number of seconds to wait before retrying the request.
    """
    def __init__(self, retry_after):
        """
        Initialize the RateLimitError.

        Args:
            retry_after (int): The number of seconds to wait before retrying the request.
        """
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Retry after {retry_after} seconds.")

class ServerError(RequestError):
    """
    Exception raised when a server error occurs.

    Attributes:
        status_code (int): The HTTP status code of the server error.
    """
    def __init__(self, status_code):
        """
        Initialize the ServerError.

        Args:
            status_code (int): The HTTP status code of the server error.
        """
        self.status_code = status_code
        super().__init__(f"Server error: {status_code}")

class GatewayTimeoutError(RequestError):
    """
    Exception raised when a gateway timeout occurs.

    Attributes:
        wait_time (int): The number of seconds to wait before retrying the request.
    """
    def __init__(self, wait_time):
        """
        Initialize the GatewayTimeoutError.

        Args:
            wait_time (int): The number of seconds to wait before retrying the request.
        """
        self.wait_time = wait_time
        super().__init__(f"Gateway timeout. Retrying after {wait_time} seconds.")

class ErrorHandler:
    def __init__(self):
        self.logger = Logger()

    def handle_error(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self.logger.log_error(f"{type(e).__name__}: {str(e)}", context=func.__qualname__)
                raise
        return wrapper

    def handle_error_with_retry(self, retry_policy, config):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                attempts = 0
                while attempts < retry_policy.max_retries:
                    try:
                        return func(*args, **kwargs)
                    except GatewayTimeoutError as e:
                        attempts += 1
                        self.qc_manager.log_warning(f"Gateway timeout occurred. Retrying in {e.wait_time} seconds...", context=func.__qualname__)
                        time.sleep(e.wait_time)
                    except (ReadTimeout, ConnectionError, Timeout) as e:
                        attempts += 1
                        wait_time = retry_policy.base_wait_time
                        self.qc_manager.log_warning(f"{type(e).__name__} occurred. Retrying in {wait_time} seconds...", context=func.__qualname__)
                        time.sleep(wait_time)
                    except ServerError as e:
                        self.qc_manager.log_error(f"Server error occurred: {e.status_code}", context=func.__qualname__)
                        raise
                    except RequestException as e:
                        self.qc_manager.log_error(f"An error occurred: {str(e)}", context=func.__qualname__)
                        raise
                self.qc_manager.log_error(f"Max retries ({retry_policy.max_retries}) exceeded.", context=func.__qualname__)
                raise Exception("Max retries exceeded")
            return wrapper
        return decorator

    def _wait_with_progress(self, wait_time, desc):
        for _ in tqdm(range(wait_time), desc=desc, unit="s", leave=False):
            time.sleep(1)