import time
from tools.qc.exceptions import *
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
        self.success_wait_time = config.get('SUCCESS_WAIT_TIME', 5)
        self.retryable_exceptions = [
            globals().get(exc_name) for exc_name in config.get('RETRYABLE_EXCEPTIONS', 
            ['NetworkException', 'RateLimitException', 'APIException'])
        ]
        self.initial_wait_times = config.get('INITIAL_WAIT_TIMES', {})

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
        
        :param config: The retry configuration
        :param attempt: The current attempt number
        :param exception: The exception that caused the retry
        :return: The calculated wait time in seconds
        """
        if isinstance(exception, RateLimitException):
            wait = config.max_wait_time
        elif attempt == 1 and isinstance(exception, APIException) and exception.status_code:
            wait = config.initial_wait_times.get(str(exception.status_code), config.base_wait_time)
        else:
            wait = min(config.base_wait_time * (config.backoff_factor ** (attempt - 1)), config.max_wait_time)
        self.qc_manager.log_debug(f"Waiting for {wait} seconds before retry", context="RetryPolicy")
        return wait

    def should_retry(self, config, exception, attempt):
        """Check if the exception should be retried based on the configuration.
        
        :param config: The retry configuration 
        :param exception: The exception to check
        :param attempt: The current attempt number
        :return: True if the exception should be retried, False otherwise
        """
        return attempt < config.max_retries and isinstance(exception, tuple(config.retryable_exceptions))

    def execute_with_retry(self, func, config_key, *args, **kwargs):
        """Execute the given function with retry logic based on the configuration.
        
        :param func: The function to execute
        :param config_key: The key of the retry configuration to use
        :param args: Positional arguments to pass to the function
        :param kwargs: Keyword arguments to pass to the function
        :return: The result of the function
        :raises: The last exception if all retries fail
        """
        config = self.get_configuration(config_key)
        attempt = 1  # Start at 1, as this is the first attempt
        last_exception = None
        
        self._local.retry_depth += 1
        outer_most = self._local.retry_depth == 1
        
        with tqdm(total=config.max_retries, desc="Retry Progress", unit="attempt", 
                  position=0, leave=True, disable=not outer_most) as pbar:
            try:
                while attempt <= config.max_retries:  # Use <= to include the last attempt
                    try:
                        result = func(*args, **kwargs)
                        self.wait_with_progress(config.success_wait_time, "Success! Waiting before next call", pbar, outer_most)
                        pbar.update(config.max_retries - attempt + 1)  # Update to fill the bar
                        return result
                    except Exception as e:
                        last_exception = e
                        if not self.should_retry(config, e, attempt) or attempt == config.max_retries:
                            pbar.update(config.max_retries - attempt + 1)  # Update to fill the bar
                            raise
                        wait_time = self.wait_time(config, attempt, e)
                        self.qc_manager.log_warning(f"Attempt {attempt} failed. Retrying in {wait_time} seconds. Error: {str(e)}", context="RetryPolicy")
                        self.wait_with_progress(wait_time, f"Retry attempt {attempt}", pbar, outer_most)
                        pbar.update(1)
                        self.qc_manager.log_debug(f"Retry wait of {wait_time} seconds completed for attempt {attempt}", context="RetryPolicy")
                        attempt += 1  # Increment attempt at the end of the loop
                
                if last_exception:
                    raise last_exception
            finally:
                self._local.retry_depth -= 1

    def wait_with_progress(self, wait_time, description, outer_pbar, show_inner_bar):
        """Wait for the specified time while updating progress bars.
        
        :param wait_time: The time to wait in seconds
        :param description: The description for the inner progress bar
        :param outer_pbar: The outer (retry) progress bar
        :param show_inner_bar: Whether to show the inner progress bar
        :return: None
        """
        if show_inner_bar:
            for _ in tqdm(range(int(wait_time)), desc=description, unit="s", leave=False):
                time.sleep(1)
                outer_pbar.refresh()
        else:
            time.sleep(wait_time)
            outer_pbar.refresh()

    def reload_configurations(self):
        """Reload all the retry configurations.
        
        :return: None
        """
        for config in self.configurations.values():
            config.reload_config()