import functools
import time
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout, ReadTimeout

class GatewayTimeoutError(Exception):
    """Exception raised for gateway timeout errors."""
    def __init__(self, wait_time):
        """
        Initialize the GatewayTimeoutError.

        Args:
            wait_time (int): The time to wait before retrying.
        """
        self.wait_time = wait_time
        super().__init__(f"Gateway timeout occurred. Wait for {wait_time} seconds before retrying.")

class RequestError(Exception):
    """Exception raised for general request errors."""
    def __init__(self, message):
        """
        Initialize the RequestError.

        Args:
            message (str): The error message.
        """
        super().__init__(message)

class ErrorHandler:
    def __init__(self, qc_manager):
        self.qc_manager = qc_manager

    def handle_error(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self.qc_manager.log_error(f"{type(e).__name__}: {str(e)}", context=func.__qualname__)
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
                    except HTTPError as e:
                        """
                        Handle HTTPError exceptions.

                        If the status code is in the 5xx range (server errors), retry the request.
                        Otherwise, log the error and raise the exception.

                        Args:
                            e (HTTPError): The HTTPError exception object.
                        """
                        if 500 <= e.response.status_code < 600:
                            attempts += 1
                            wait_time = retry_policy.base_wait_time
                            self.qc_manager.log_warning(f"HTTP {e.response.status_code} error occurred. Retrying in {wait_time} seconds...", context=func.__qualname__)
                            time.sleep(wait_time)
                        else:
                            self.qc_manager.log_error(f"HTTP error occurred: {e.response.status_code}", context=func.__qualname__)
                            raise
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
        """
        Wait for a specified time with a progress bar using tqdm.

        Args:
            wait_time (int): The number of seconds to wait.
            desc (str): The description to display on the progress bar.
        """
        for _ in tqdm(range(wait_time), desc=desc, unit="s", leave=False):
            time.sleep(1)