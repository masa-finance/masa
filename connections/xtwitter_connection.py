from connections.api_connection import APIConnection
from configs.config import XTwitterConfig
from masa_tools.qc.error_handler import ErrorHandler
from masa_tools.qc.logging import Logger
from urllib.parse import urlparse
import time

class XTwitterConnection(APIConnection):
    """
    A class for handling connections to the Twitter API through the MASA Oracle.

    This class extends the APIConnection class and provides specific functionality
    for interacting with the Twitter API, including request retries and error handling.

    :param APIConnection: The base class for API connections.
    """

    def __init__(self):
        """
        Initialize the XTwitterConnection instance.

        This method sets up the connection parameters using the XTwitterConfig,
        initializes the base APIConnection, and sets up the error handler.

        :raises KeyError: If the 'BASE_URL' key is not found in the environment variables.
        """
        config = XTwitterConfig()
        twitter_config = config.get_config()
        self.logger = Logger("XTwitterConnection")
        
        base_url = config.get_env_var('BASE_URL')
        headers = twitter_config['headers']
        self.timeout = twitter_config['request_timeout']
        self.max_retries = twitter_config['max_retries']
        self.retry_delay = twitter_config['retry_delay']
        
        super().__init__(base_url, headers)
        
        self.error_handler = ErrorHandler(self.logger)

    @ErrorHandler.handle_error
    def make_request(self, endpoint, method='GET', data=None):
        """
        Make a request to the specified endpoint of the MASA Oracle for Twitter data.

        This method handles request retries and error checking.

        :param endpoint: The endpoint of the MASA Oracle.
        :type endpoint: str
        :param method: The HTTP method to use for the request, defaults to 'GET'.
        :type method: str, optional
        :param data: The data to send with the request, defaults to None.
        :type data: dict, optional
        :return: The response from the MASA Oracle.
        :rtype: requests.Response
        :raises InvalidURL: If the constructed URL is invalid.
        :raises UnexpectedStatusCode: If the response status code is unexpected.
        :raises MaxRetriesExceeded: If the maximum number of retries is exceeded.
        """
        endpoint = endpoint.lstrip('/')
        self.base_url = self.base_url.rstrip('/')
        
        url = f"{self.base_url}/{endpoint}"
        if not self.is_valid_url(url):
            url = self.fix_url(url)
            if not self.is_valid_url(url):
                self.error_handler.raise_error("InvalidURL", f"Invalid URL: {url}")
        
        attempts = 0
        while attempts < self.max_retries:
            response = super().make_request(endpoint, method, data)
            if response.status_code == 200:
                return response
            elif response.status_code == 504:
                time.sleep(self.retry_delay)
                attempts += 1
            else:
                self.error_handler.raise_error("UnexpectedStatusCode", f"Unexpected status code: {response.status_code}")
        
        self.error_handler.raise_error("MaxRetriesExceeded", f"Failed to make request to {url} after {self.max_retries} attempts.")

    def is_valid_url(self, url):
        """
        Check if the given URL is valid.

        :param url: The URL to check.
        :type url: str
        :return: True if the URL is valid, False otherwise.
        :rtype: bool
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def fix_url(self, url):
        """
        Attempt to fix an invalid URL.

        :param url: The URL to fix.
        :type url: str
        :return: The fixed URL.
        :rtype: str
        """
        # Implement URL fixing logic here
        pass