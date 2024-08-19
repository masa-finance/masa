import requests
from masa.qc.logging import Logger
from masa.qc.error_handler import ErrorHandler
from requests.exceptions import ReadTimeout, ConnectionError, RequestException
import time

class APIConnection:
    """
    A class for handling API connections and requests.
    """

    def __init__(self, base_url, headers=None, timeout=30, max_retries=3, retry_delay=960):
        """
        Initialize the APIConnection instance.

        :param base_url: The base URL of the API.
        :type base_url: str
        :param headers: The headers to include in the requests (optional).
        :type headers: dict
        :param timeout: The request timeout in seconds (default is 30).
        :type timeout: int
        :param max_retries: The maximum number of retries for failed requests (default is 3).
        :type max_retries: int
        :param retry_delay: The delay in seconds between retries (default is 960).
        :type retry_delay: int
        """
        self.base_url = base_url
        self.headers = headers
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = Logger("APIConnection")
        self.error_handler = ErrorHandler(self.logger)

    @ErrorHandler.handle_error
    def make_request(self, endpoint, method='GET', data=None):
        """
        Make an API request to the specified endpoint.

        :param endpoint: The endpoint of the API.
        :type endpoint: str
        :param method: The HTTP method to use for the request (default is 'GET').
        :type method: str
        :param data: The data to send with the request (optional).
        :type data: dict
        :return: The response from the API.
        :rtype: requests.Response
        """
        url = f"{self.base_url}/{endpoint}"
        attempts = 0
        while attempts < self.max_retries:
            try:
                response = requests.request(method, url, json=data, headers=self.headers, timeout=self.timeout)
                if response.status_code == 200:
                    self.logger.log_info(f"API request successful: {method} {url}")
                    return response
                elif response.status_code == 504:
                    self.logger.log_warning(f"Received 504 error for {url}. Pausing before retrying...")
                    time.sleep(self.retry_delay)
                    attempts += 1
                else:
                    response.raise_for_status()  # Raise an exception for other 4xx or 5xx status codes
            except (ReadTimeout, ConnectionError, RequestException) as e:
                error_details = {
                    "url": url,
                    "method": method,
                    "data": data,
                    "headers": self.headers,
                    "timeout": self.timeout,
                    "attempt": attempts + 1,
                    "max_retries": self.max_retries
                }
                self.error_handler.raise_error(type(e).__name__, str(e), error_details)
                time.sleep(self.retry_delay)
                attempts += 1
        
        self.error_handler.raise_error("MaxRetriesExceeded", f"Failed to make request to {url} after {self.max_retries} attempts.")

    def get(self, endpoint, params=None):
        """
        Make a GET request to the specified endpoint.

        :param endpoint: The endpoint of the API.
        :type endpoint: str
        :param params: The query parameters to include in the request (optional).
        :type params: dict
        :return: The response from the API.
        :rtype: requests.Response
        """
        return self.make_request(endpoint, method='GET', data=params)

    def post(self, endpoint, data):
        """
        Make a POST request to the specified endpoint.

        :param endpoint: The endpoint of the API.
        :type endpoint: str
        :param data: The data to send with the request.
        :type data: dict
        :return: The response from the API.
        :rtype: requests.Response
        """
        return self.make_request(endpoint, method='POST', data=data)