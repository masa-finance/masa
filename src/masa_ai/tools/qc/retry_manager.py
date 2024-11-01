import time
from .exceptions import *
from tqdm.auto import tqdm
import threading

class RetryConfiguration:
    def __init__(self, config_key, settings):
        self.config_key = config_key
        self.settings = settings
        self.reload_config()

    def reload_config(self):
        """Reload the retry configuration from the settings.
        
        :return: None
        """
        config = self.settings.get(self.config_key, {})
        self.max_retries = config.get('MAX_RETRIES', 3)
        self.base_wait_time = config.get('BASE_WAIT_TIME', 10)
        self.backoff_factor = config.get('BACKOFF_FACTOR', 2)
        self.max_wait_time = config.get('MAX_WAIT_TIME', 960)
        self.initial_wait_times = config.get('INITIAL_WAIT_TIMES', {})
        self.success_wait_time = config.get('SUCCESS_WAIT_TIME', 10)
        
        # Ensure only valid exception classes are included
        self.retryable_exceptions = [
            globals()[exc_name] for exc_name in config.get(
                'RETRYABLE_EXCEPTIONS', 
                ['NetworkException', 'RateLimitException', 'APIException', 
                 'NoWorkersAvailableException', 'GatewayTimeoutException']
            ) if exc_name in globals()
        ]


class RetryPolicy:
    def __init__(self, settings, qc_manager):
        self.settings = settings
        self.qc_manager = qc_manager
        self.configurations = {}
        self._local = threading.local()
        self._local.retry_depth = 0

    def get_configuration(self, config_key):
        """Get the retry configuration for the given key.
        
        :param config_key: The key of the configuration
        :return: The retry configuration
        """
        if config_key not in self.configurations:
            self.configurations[config_key] = RetryConfiguration(config_key, self.settings)
        return self.configurations[config_key]

    def wait_time(self, config, attempt, exception):
        """Calculate the wait time based on the retry configuration and attempt.

        Args:
            config (RetryConfiguration): The retry configuration.
            attempt (int): The current attempt number.
            exception (Exception): The exception that caused the retry.

        Returns:
            float: The calculated wait time in seconds.
        """
        # Determine the initial wait time based on the exception type
        if isinstance(exception, APIException) and hasattr(exception, 'status_code'):
            status_code = str(exception.status_code)
            initial_wait = config.initial_wait_times.get(status_code, config.base_wait_time)
        elif isinstance(exception, RateLimitException):
            initial_wait = config.initial_wait_times.get('429', config.base_wait_time)
        elif isinstance(exception, NoWorkersAvailableException):
            initial_wait = config.initial_wait_times.get('417', config.base_wait_time)
        elif isinstance(exception, GatewayTimeoutException):
            initial_wait = config.initial_wait_times.get('504', config.base_wait_time)
        else:
            initial_wait = config.base_wait_time

        # Calculate the wait time using exponential backoff
        if attempt == 1:
            wait = initial_wait
        else:
            wait = min(initial_wait * (config.backoff_factor ** (attempt - 1)), config.max_wait_time)

        # Log the calculated wait time
        self.qc_manager.log_debug(
            f"Calculated wait time: {wait} seconds before retrying (Attempt {attempt})",
            context="RetryPolicy.wait_time"
        )
        return wait

    def should_retry(self, config, exception, attempt):
        """Check if the exception should be retried based on the configuration.
        
        Args:
            config (RetryConfiguration): The retry configuration.
            exception (Exception): The exception to check.
            attempt (int): The current attempt number.

        Returns:
            bool: True if the exception should be retried, False otherwise.
        """
        # Determine if the exception is retryable and if the max retries have not been exceeded
        return attempt < config.max_retries and isinstance(exception, tuple(config.retryable_exceptions))

    def execute_with_retry(self, func, config_key, *args, **kwargs):
        """
        Execute the given function with retry logic based on the configuration.

        Args:
            func (callable): The function to execute.
            config_key (str): The key of the retry configuration to use.
            args: Positional arguments to pass to the function.
            kwargs: Keyword arguments to pass to the function.

        Returns:
            Any: The result of the function.

        Raises:
            Exception: The last exception if all retries fail.
        """
        config = self.get_configuration(config_key)
        attempt = 1
        last_exception = None

        while attempt <= config.max_retries:
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                last_exception = e
                if not self.should_retry(config, e, attempt):
                    raise
                wait_time = self.wait_time(config, attempt, e)
                self.qc_manager.log_warning(f"Attempt {attempt} failed. Retrying in {wait_time} seconds. Error: {str(e)}", context="RetryPolicy")
                self.wait_with_progress(wait_time)
                attempt += 1

        if last_exception:
            raise last_exception

    def wait_with_progress(self, wait_time):
        """
        Wait for the specified time while showing a progress bar.

        :param wait_time: The time to wait in seconds
        """
        with tqdm(total=wait_time, desc="Wait Time", unit="s", leave=False) as pbar:
            start_time = time.time()
            while time.time() - start_time < wait_time:
                time.sleep(0.2)
                elapsed = time.time() - start_time
                update_value = min(elapsed - pbar.n, wait_time - pbar.n)
                pbar.update(update_value)
            pbar.update(wait_time - pbar.n)

    def reload_configurations(self):
        """Reload all the retry configurations.
        
        :return: None
        """
        for config in self.configurations.values():
            config.reload_config()
