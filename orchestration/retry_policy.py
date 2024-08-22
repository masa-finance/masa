import time
from datetime import datetime, timedelta

class RetryPolicy:
    def __init__(self, max_retries=3, base_wait_time=60, max_wait_time=960, gateway_timeout_wait_time=960):
        """
        Initialize the RetryPolicy.

        :param max_retries: The maximum number of retries, defaults to 3.
        :type max_retries: int, optional
        :param base_wait_time: The base wait time in seconds, defaults to 60.
        :type base_wait_time: int, optional
        :param max_wait_time: The maximum wait time in seconds, defaults to 960.
        :type max_wait_time: int, optional
        :param gateway_timeout_wait_time: The wait time in seconds for gateway timeout errors, defaults to 960.
        :type gateway_timeout_wait_time: int, optional
        """
        self.max_retries = max_retries
        self.base_wait_time = base_wait_time
        self.max_wait_time = max_wait_time
        self.gateway_timeout_wait_time = gateway_timeout_wait_time

    def wait_time(self, retry_count, status_code=None):
        """
        Calculate the wait time based on the retry count and status code.

        :param retry_count: The current retry count.
        :type retry_count: int
        :param status_code: The HTTP status code of the response, defaults to None.
        :type status_code: int, optional
        :return: The calculated wait time in seconds.
        :rtype: int
        """
        if status_code == 504:
            return self.gateway_timeout_wait_time
        else:
            wait = min(self.base_wait_time * (2 ** retry_count), self.max_wait_time)
            return wait