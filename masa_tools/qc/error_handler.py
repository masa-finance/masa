import functools
import traceback
import time
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout, ReadTimeout
from .logging import Logger
from tqdm import tqdm

class RequestError(Exception):
    def __init__(self, message: str, method: str, url: str, status_code: int = None):
        self.message = message
        self.method = method
        self.url = url
        self.status_code = status_code
        super().__init__(self.message)

    def __str__(self):
        status_info = f", Status Code: {self.status_code}" if self.status_code else ""
        return f"RequestError: {self.message} (Method: {self.method}, URL: {self.url}{status_info})"

class GatewayTimeoutError(RequestError):
    def __init__(self, message: str, url: str, timeout: float):
        super().__init__(message, "Unknown", url)
        self.timeout = timeout

    def __str__(self):
        return f"GatewayTimeoutError: {self.message} (URL: {self.url}, Timeout: {self.timeout}s)"

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
                    except (ReadTimeout, ConnectionError, Timeout) as e:
                        attempts += 1
                        self.logger.log_warning(f"{type(e).__name__} occurred. Retrying in {config['TWITTER_RETRY_DELAY']} seconds...", context=func.__qualname__)
                        time.sleep(config['TWITTER_RETRY_DELAY'])
                    except RequestException as e:
                        self.logger.log_error(f"An error occurred: {str(e)}", context=func.__qualname__)
                        raise
                self.logger.log_error(f"Max retries ({retry_policy.max_retries}) exceeded.", context=func.__qualname__)
                raise Exception("Max retries exceeded")
            return wrapper
        return decorator