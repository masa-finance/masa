import time
from masa_tools.qc.qc_manager import QCManager
from masa_tools.qc.exceptions import *
from configs.config import global_settings

class RetryConfiguration:
    def __init__(self, config_key):
        self.config_key = config_key
        self.reload_config()

    def reload_config(self):
        """Reload the retry configuration from the global settings."""
        config = global_settings.get(self.config_key)
        self.max_retries = config.get('MAX_RETRIES', 3)
        self.base_wait_time = config.get('BASE_WAIT_TIME', 10)
        self.backoff_factor = config.get('BACKOFF_FACTOR', 2)
        self.max_wait_time = config.get('MAX_WAIT_TIME', 960)
        self.success_wait_time = config.get('SUCCESS_WAIT_TIME', 0)  # Added success wait time
        self.retryable_exceptions = [
            globals().get(exc_name) for exc_name in config.get('RETRYABLE_EXCEPTIONS', 
            ['NetworkException', 'RateLimitException', 'APIException'])
        ]
        self.initial_wait_times = config.get('INITIAL_WAIT_TIMES', {})

class RetryPolicy:
    def __init__(self):
        self.qc_manager = QCManager()
        self.configurations = {}

    def get_configuration(self, config_key):
        """Get the retry configuration for the given key."""
        if config_key not in self.configurations:
            self.configurations[config_key] = RetryConfiguration(config_key)
        return self.configurations[config_key]

    def wait_time(self, config, attempt, error_code=None):
        """Calculate the wait time based on the retry configuration and attempt."""
        if attempt == 1 and error_code and str(error_code) in config.initial_wait_times:
            wait = config.initial_wait_times[str(error_code)]
        else:
            wait = min(config.base_wait_time * (config.backoff_factor ** (attempt - 1)), config.max_wait_time)
        self.qc_manager.debug(f"Waiting for {wait} seconds before retry", context="RetryPolicy")
        return wait

    def should_retry(self, config, exception, attempt):
        """Check if the exception should be retried based on the configuration."""
        return attempt < config.max_retries and isinstance(exception, tuple(config.retryable_exceptions))

    def execute_with_retry(self, func, config_key, *args, **kwargs):
        """Execute the given function with retry logic based on the configuration."""
        config = self.get_configuration(config_key)
        attempt = 0
        last_exception = None
        while attempt < config.max_retries:
            try:
                result = func(*args, **kwargs)
                time.sleep(config.success_wait_time)  # Wait after successful execution
                return result
            except Exception as e:
                attempt += 1
                last_exception = e
                if not self.should_retry(config, e, attempt):
                    raise
                error_code = getattr(e, 'status_code', None)
                wait_time = self.wait_time(config, attempt, error_code)
                self.qc_manager.log_warning(f"Attempt {attempt} failed. Retrying in {wait_time} seconds. Error: {str(e)}", context="RetryPolicy")
                time.sleep(wait_time)
        
        if last_exception:
            raise last_exception

    def reload_configurations(self):
        """Reload all the retry configurations."""
        for config in self.configurations.values():
            config.reload_config()