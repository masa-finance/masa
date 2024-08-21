from masa.connections.api_connection import APIConnection
from masa.configs.config import Config
from masa.qc.error_handler import ErrorHandler
from masa.utils.state_manager import StateManager  # Import the StateManager
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
        config = Config()
        twitter_config = config.get_twitter_config()
        
        base_url = config.get_env_var('BASE_URL')  # Get the base URL from environment variables
        headers = twitter_config['headers']
        self.timeout = twitter_config['request_timeout']
        self.max_retries = twitter_config['max_retries']
        self.retry_delay = twitter_config['retry_delay']
        
        super().__init__(base_url, headers)
        
        self.state_manager = StateManager()  # Create an instance of StateManager

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
        """
        url = f"{self.base_url}/{endpoint}"
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