import time
from masa_tools.qc.exceptions import *
from tqdm import tqdm

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
            ['NetworkException', 'RateLimitException', 'APIException', 'TooManyRequestsException'])
        ]
        self.initial_wait_times = config.get('INITIAL_WAIT_TIMES', {})

class RetryPolicy:
    def __init__(self, settings, qc_manager):
        self.settings = settings
        self.qc_manager = qc_manager
        self.configurations = {}

    def get_configuration(self, config_key):
        """Get the retry configuration for the given key."""
        if config_key not in self.configurations:
            self.configurations[config_key] = RetryConfiguration(config_key, self.settings)
        return self.configurations[config_key]

    def wait_time(self, config, attempt, exception):
        """Calculate the wait time based on the retry configuration and attempt."""
        if isinstance(exception, TooManyRequestsException):
            # For 429 errors, use the maximum wait time
            wait = config.max_wait_time
        elif attempt == 1 and isinstance(exception, APIException) and exception.status_code:
            # Check for initial wait times based on status code
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
        while attempt < config.max_retries:
            try:
                result = func(*args, **kwargs)
                # Wait after successful execution and log progress with tqdm
                for _ in tqdm(range(config.success_wait_time), desc="Success Wait", unit="s"):
                    time.sleep(1)
                self.qc_manager.log_info(f"Success! Waiting for {config.success_wait_time} seconds before next call.", context="RetryPolicy")
                return result
            except Exception as e:
                attempt += 1
                last_exception = e
                if not self.should_retry(config, e, attempt):
                    raise
                wait_time = self.wait_time(config, attempt, e)
                self.qc_manager.log_warning(f"Attempt {attempt} failed. Retrying in {wait_time} seconds. Error: {str(e)}", context="RetryPolicy")
                # Wait before retrying and log progress with tqdm
                for _ in tqdm(range(wait_time), desc=f"Retry Wait (Attempt {attempt})", unit="s"):
                    time.sleep(1)
                self.qc_manager.log_info(f"Retry wait of {wait_time} seconds completed for attempt {attempt}", context="RetryPolicy")
        
        if last_exception:
            raise last_exception

    def reload_configurations(self):
        """Reload all the retry configurations."""
        for config in self.configurations.values():
            config.reload_config()