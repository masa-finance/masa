import time
from masa_tools.qc.qc_manager import QCManager
from tqdm import tqdm

class RetryPolicy:
    def __init__(self, max_retries=3, base_wait_time=60, max_wait_time=960, timeout=30, success_interval=7):
        """
        Initialize the RetryPolicy.

        :param max_retries: The maximum number of retries, defaults to 3.
        :param base_wait_time: The base wait time in seconds, defaults to 60.
        :param max_wait_time: The maximum wait time in seconds, defaults to 960.
        :param timeout: The timeout for requests in seconds, defaults to 30.
        :param success_interval: The interval to wait after successful retrieval, defaults to 7.
        """
        self.max_retries = max_retries
        self.base_wait_time = base_wait_time
        self.max_wait_time = max_wait_time
        self.timeout = timeout
        self.success_interval = success_interval
        self.qc_manager = QCManager()

    def wait_time(self, retry_count):
        """
        Calculate the wait time based on the retry count.

        :param retry_count: The current retry count.
        :return: The calculated wait time in seconds.
        """
        return min(self.base_wait_time * (2 ** retry_count), self.max_wait_time)

    def wait_after_success(self):
        """
        Wait for the success interval.
        """
        self.qc_manager.log_debug(f"Waiting for {self.success_interval} seconds after successful retrieval", context="RetryPolicy")
        with tqdm(total=self.success_interval, desc="Waiting", unit="s") as pbar:
            for _ in range(self.success_interval):
                time.sleep(1)
                pbar.update(1)

    def execute_with_retry(self, func, *args, **kwargs):
        """
        Execute a function with retries.

        :param func: The function to execute.
        :param args: Positional arguments for the function.
        :param kwargs: Keyword arguments for the function.
        :return: The result of the function execution.
        :raises Exception: If the maximum number of retries is exceeded.
        """
        retries = 0
        while retries <= self.max_retries:
            try:
                result = func(*args, **kwargs)
                self.wait_after_success()
                return result
            except Exception as e:
                retries += 1
                if retries > self.max_retries:
                    raise
                wait_time = self.wait_time(retries)
                self.qc_manager.log_warning(f"Retry {retries}/{self.max_retries}. Waiting for {wait_time} seconds.", context="RetryPolicy")
                
                # Create a tqdm progress bar
                with tqdm(total=wait_time, desc="Waiting", unit="s") as pbar:
                    for _ in range(wait_time):
                        time.sleep(1)
                        pbar.update(1)
                        # Log the remaining time every 10 seconds
                        if pbar.n % 10 == 0:
                            remaining_time = wait_time - pbar.n
                            self.qc_manager.log_info(f"Remaining wait time: {remaining_time} seconds", context="RetryPolicy")

    def get_retry_count(self):
        return self.current_retry_count