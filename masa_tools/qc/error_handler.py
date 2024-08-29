import functools
import sys
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout
from .exceptions import (
    MASAException,
    APIException,
    NetworkException,
    RateLimitException,
    AuthenticationException,
    TooManyRequestsException
)

class ErrorHandler:
    def __init__(self, qc_manager):
        self.qc_manager = qc_manager

    def handle_error(self, func):
        """
        Decorator to handle errors in a function.

        :param func: The function to decorate.
        :return: The decorated function.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except MASAException as e:
                self.qc_manager.log_error(f"{type(e).__name__}: {str(e)}", error_info=e, context=func.__qualname__)
                raise
            except Exception as e:
                self.qc_manager.log_error(f"Unexpected error: {type(e).__name__}: {str(e)}", error_info=e, context=func.__qualname__)
                raise MASAException(f"Unexpected error in {func.__qualname__}: {str(e)}") from e
        return wrapper

    def handle_error_with_retry(self, config_key):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return self.qc_manager.execute_with_retry(
                    self._api_call_with_error_handling,
                    config_key,
                    func, *args, **kwargs
                )
            return wrapper
        return decorator

    def _api_call_with_error_handling(self, func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TooManyRequestsException as e:
            # Re-raise TooManyRequestsException without wrapping it
            raise
        except RequestException as e:
            if isinstance(e, ConnectionError):
                raise NetworkException(f"Network error: {str(e)}", status_code=None) from e
            elif isinstance(e, Timeout):
                raise NetworkException(f"Request timed out: {str(e)}", status_code=None) from e
            elif isinstance(e, HTTPError):
                status_code = e.response.status_code
                if status_code == 404:
                    self.qc_manager.log_error(f"Received 404 error. Exiting program.", error_info=e)
                    sys.exit(1)  # Exit the program on 404 error
                elif status_code == 429:
                    raise TooManyRequestsException("Too many requests", status_code=status_code) from e
                elif status_code in (401, 403):
                    raise AuthenticationException("Authentication failed", status_code=status_code) from e
                else:
                    raise APIException(f"HTTP error {status_code}: {str(e)}", status_code=status_code) from e
            else:
                raise APIException(f"API request failed: {str(e)}", status_code=None) from e
        except Exception as e:
            self.qc_manager.log_error(f"Unexpected error in API call: {type(e).__name__}: {str(e)}", error_info=e.__traceback__, context=func.__qualname__)
            raise APIException(f"Unexpected error in API call: {str(e)}", status_code=None) from e