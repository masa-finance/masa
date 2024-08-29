from .api_connection import APIConnection
from configs.config import global_settings
from masa_tools.qc.qc_manager import QCManager
from masa_tools.utils.helper_functions import format_url

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
        self.base_url = global_settings.get('twitter.BASE_URL') or global_settings.get('twitter.BASE_URL_LOCAL')
        if not self.base_url:
            raise ValueError("Twitter base URL is not configured")
        self.qc_manager.log_debug(f"Initialized XTwitterConnection with base URL: {self.base_url}", context="XTwitterConnection")

    def get_headers(self):
        """
        Get headers for XTwitter API requests.

        Returns:
            dict: A dictionary of headers to be used in the API request.
        """
        return global_settings.get('twitter.HEADERS', {})  # Get headers from global settings

    @QCManager().handle_error
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

    @QCManager().handle_error_with_retry('twitter.RETRY_CONFIG')
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
        url = format_url(self.base_url, endpoint)
        self.qc_manager.log_debug(f"Making request to URL: {url}", context="XTwitterConnection")
        return self._make_request(method, url, data=data)

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