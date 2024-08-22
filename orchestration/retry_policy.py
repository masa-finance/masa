import time
from datetime import datetime, timedelta

class RetryPolicy:
    def __init__(self, max_retries=3, base_wait_time=60, max_wait_time=960):
        self.max_retries = max_retries
        self.base_wait_time = base_wait_time
        self.max_wait_time = max_wait_time

    def wait_time(self, retry_count):
        wait = min(self.base_wait_time * (2 ** retry_count), self.max_wait_time)
        return wait