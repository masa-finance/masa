from .api_connection import APIConnection
from configs.config import global_settings
from masa_tools.qc.qc_manager import QCManager
from masa_tools.utils.helper_functions import format_url
from masa_tools.qc.exceptions import AuthenticationException, APIException, RateLimitException

class XTwitterConnection(APIConnection):
    """
    XTwitter API connection class.

    This class implements the APIConnection interface for the XTwitter API.
    It handles XTwitter-specific configuration, headers, timeouts, and response handling.
    """

    def __init__(self):
        """Initialize the XTwitterConnection."""
        self.qc_manager = QCManager()
        
        super().__init__()
        self.base_url = global_settings.get('twitter.BASE_URL') or global_settings.get('twitter.BASE_URL_LOCAL')

    def get_headers(self):
        """
        Get headers for XTwitter API requests.

        Returns:
            dict: A dictionary of headers to be used in the API request.
        """
        return global_settings.get('twitter.HEADERS', {})  # Get headers from global settings

    def get_tweets(self, endpoint, query, count):
        """
        Get tweets from the XTwitter API.

        Args:
            endpoint (str): The API endpoint to request.
            query (str): The search query for tweets.
            count (int): The number of tweets to retrieve.

        Returns:
            dict: The processed response data.
        """
        data = {'query': query, 'count': count}
        response = self.make_request(endpoint, method='POST', data=data)
        return self.handle_response(response)

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
        elif response.status_code == 429:
            raise RateLimitException("Rate limit exceeded", status_code=response.status_code)
        elif response.status_code in (401, 403):
            raise AuthenticationException("Authentication failed", status_code=response.status_code)
        else:
            raise APIException(f"HTTP error {response.status_code}: {response.text}", status_code=response.status_code)