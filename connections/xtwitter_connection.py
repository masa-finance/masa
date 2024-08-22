from connections.api_connection import APIConnection
from configs.config import XTwitterConfig
from masa_tools.qc.error_handler import ErrorHandler
from masa_tools.utils.state_manager import StateManager  # Import the StateManager
from urllib.parse import urlparse, urlunparse
import time

class XTwitterConnection(APIConnection):
    """
    A class for handling connections to the Twitter API through the MASA Oracle.
    """

    def __init__(self):
        """
        Initialize the XTwitterConnection instance.
        
        :raises KeyError: If the 'BASE_URL' key is not found in the environment variables.
        """
        config = XTwitterConfig()
        twitter_config = config.get_config()
        
        base_url = config.get_env_var('BASE_URL')  # Get the base URL from environment variables
        headers = twitter_config['headers']
        self.timeout = twitter_config['request_timeout']
        self.max_retries = twitter_config['max_retries']
        self.retry_delay = twitter_config['retry_delay']
        
        super().__init__(base_url, headers)
        
        # self.state_manager = StateManager()  # Create an instance of StateManager

    @ErrorHandler.handle_error
    def make_request(self, endpoint, method='GET', data=None):
        """
        Make a request to the specified endpoint of the MASA Oracle for Twitter data.

        :param endpoint: The endpoint of the MASA Oracle. 
        :type endpoint: str
        :param method: The HTTP method to use for the request (default is 'GET').
        :type method: str
        :param data: The data to send with the request (optional).
        :type data: dict
        :return: The response from the MASA Oracle.
        :rtype: requests.Response
        :raises UnexpectedStatusCode: If the response status code is not 200 after retries.
        :raises MaxRetriesExceeded: If the maximum number of retries is exceeded.
        """

        endpoint = endpoint.lstrip('/')
        self.base_url = self.base_url.rstrip('/') # TODO: Make a more sophisticated URL builder

        
        url = f"{self.base_url}/{endpoint}"
        # Check if the URL is valid
        if not self.is_valid_url(url):
            # Attempt to fix the URL
            url = self.fix_url(url)
            if not self.is_valid_url(url):
                error_details = {
                    "url": url,
                    "method": method,
                    "data": data,
                    "headers": self.headers
                }
                self.error_handler.raise_error("InvalidURL", f"Invalid URL: {url}", error_details)
        
        attempts = 0
        while attempts < self.max_retries:
            response = super().make_request(endpoint, method, data)
            if response.status_code == 200:
                self.logger.log_info(f"Request to MASA Oracle successful: {method} {url}")
                return response
            elif response.status_code == 504:
                self.logger.log_warning(f"Received 504 error for {url}. Pausing before retrying...")
                time.sleep(self.retry_delay)
                attempts += 1
            else:
                error_details = {
                    "url": url,
                    "method": method,
                    "data": data,
                    "headers": self.headers,
                    "status_code": response.status_code
                }
                self.error_handler.raise_error("UnexpectedStatusCode", f"Unexpected status code: {response.status_code}", error_details)
        
        error_details = {
            "url": url,
            "method": method,
            "data": data,
            "headers": self.headers,
            "max_retries": self.max_retries
        }
        self.error_handler.raise_error("MaxRetriesExceeded", f"Failed to make request to {url} after {self.max_retries} attempts.", error_details)
    
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