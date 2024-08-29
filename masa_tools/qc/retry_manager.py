import time
from masa_tools.qc.exceptions import *
from tqdm import tqdm
import threading

class RetryConfiguration:
    def __init__(self, config_key, settings):
        self.config_key = config_key
        self.settings = settings
        self.reload_config()

    def reload_config(self):
        """Reload the retry configuration from the settings."""
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
        """Get the retry configuration for the given key."""
        if config_key not in self.configurations:
            self.configurations[config_key] = RetryConfiguration(config_key, self.settings)
        return self.configurations[config_key]

    def wait_time(self, config, attempt, exception):
        """Calculate the wait time based on the retry configuration and attempt."""
        if isinstance(exception, RateLimitException):
            wait = config.max_wait_time
        elif attempt == 1 and isinstance(exception, APIException) and exception.status_code:
            wait = config.initial_wait_times.get(str(exception.status_code), config.base_wait_time)
        else:
            wait = min(config.base_wait_time * (config.backoff_factor ** (attempt - 1)), config.max_wait_time)
        self.qc_manager.log_debug(f"Waiting for {wait} seconds before retry", context="RetryPolicy")
        return wait

    def should_retry(self, config, exception, attempt):
        """Check if the exception should be retried based on the configuration."""
        return attempt < config.max_retries and isinstance(exception, tuple(config.retryable_exceptions))

    def execute_with_retry(self, func, config_key, *args, **kwargs):
        """Execute the given function with retry logic based on the configuration."""
        config = self.get_configuration(config_key)
        attempt = 0
        last_exception = None
        
        self._local.retry_depth += 1
        outer_most = self._local.retry_depth == 1
        
        pbar = tqdm(total=config.max_retries, desc="Retry Progress", unit="attempt", 
                    position=0, leave=True, disable=not outer_most)
        
        try:
            while attempt < config.max_retries:
                try:
                    result = func(*args, **kwargs)
                    self.wait_with_progress(config.success_wait_time, "Success! Waiting before next call", pbar, outer_most)
                    pbar.update(config.max_retries - attempt)
                    return result
                except Exception as e:
                    attempt += 1
                    last_exception = e
                    if not self.should_retry(config, e, attempt):
                        pbar.update(config.max_retries - attempt)
                        raise
                    wait_time = self.wait_time(config, attempt, e)
                    self.qc_manager.log_warning(f"Attempt {attempt} failed. Retrying in {wait_time} seconds. Error: {str(e)}", context="RetryPolicy")
                    self.wait_with_progress(wait_time, f"Retry attempt {attempt}", pbar, outer_most)
                    pbar.update(1)
                    self.qc_manager.log_debug(f"Retry wait of {wait_time} seconds completed for attempt {attempt}", context="RetryPolicy")
        
            if last_exception:
                raise last_exception
        finally:
            self._local.retry_depth -= 1
            if outer_most:
                pbar.close()

    def wait_with_progress(self, wait_time, description, outer_pbar, show_inner_bar):
        if show_inner_bar:
            with tqdm(total=int(wait_time), desc=description, unit="s", leave=False) as inner_pbar:
                for _ in range(int(wait_time)):
                    time.sleep(1)
                    inner_pbar.update(1)
                    outer_pbar.refresh()
        else:
            time.sleep(wait_time)
            outer_pbar.refresh()

    def reload_configurations(self):
        """Reload all the retry configurations."""
        for config in self.configurations.values():
            config.reload_config()