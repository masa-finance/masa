from .api_connection import APIConnection
from configs.config import global_settings
from masa_tools.qc.qc_manager import QCManager

class XTwitterConnection(APIConnection):
    """
    XTwitter API connection class.

    This class implements the APIConnection interface for the XTwitter API.
    It handles XTwitter-specific configuration, headers, timeouts, and response handling.
    """

    def __init__(self):
        """Initialize the XTwitterConnection."""
        self.qc_manager = QCManager()
        self.qc_manager.log_debug("Initializing XTwitterConnection", context="XTwitterConnection")
        
        super().__init__()
        self.qc_manager.log_debug("XTwitterConnection initialized successfully", context="XTwitterConnection")

    def get_headers(self):
        """
        Get headers for XTwitter API requests.

        Returns:
            dict: A dictionary of headers to be used in the API request.
        """
        return global_settings.get('twitter.HEADERS', {})  # Get headers from global settings

    def get_timeout(self):
        """
        Get timeout for XTwitter API requests.

        Returns:
            int: The timeout value in seconds for the API request.
        """
        return self.config.get('request_timeout', 30)

    @QCManager.handle_error
    def handle_response(self, response):
        """
        Handle the XTwitter API response.

        Args:
            response (requests.Response): The response object from the API request.

        Returns:
            dict: The processed response data.
        """
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    @QCManager.handle_error_with_retry('twitter.RETRY_CONFIG')
    def make_request(self, endpoint, method='POST', data=None):
        """
        Make a request to the XTwitter API.

        Args:
            endpoint (str): The API endpoint to request.
            method (str, optional): The HTTP method for the request. Defaults to 'POST'.
            data (dict, optional): The data to send in the request body.

        Returns:
            requests.Response: The raw response object from the API request.
        """
        return self._make_request(method, endpoint, data=data)

    def get_tweets(self, endpoint, query, count):
        """
        Get tweets from the XTwitter API.

        Args:
            endpoint (str): The API endpoint to request.
            query (str): The search query for tweets.
            count (int): The number of tweets to retrieve.

        Returns:
            requests.Response: The raw response object from the API request.
        """
        data = {'query': query, 'count': count}
        return self.make_request(endpoint, method='POST', data=data)