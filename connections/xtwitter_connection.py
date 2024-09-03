"""
Module for handling connections to the XTwitter API in the MASA project.

This module provides a concrete implementation of the APIConnection class
specifically for interacting with the XTwitter API. It handles authentication,
request formatting, and response processing for XTwitter-specific endpoints.
"""

from .api_connection import APIConnection
from configs.config import global_settings
from tools.qc.qc_manager import QCManager
from tools.utils.helper_functions import format_url
from tools.qc.exceptions import AuthenticationException, APIException, RateLimitException

class XTwitterConnection(APIConnection):
    """
    XTwitter API connection class.

    This class implements the APIConnection interface for the XTwitter API.
    It handles XTwitter-specific configuration, headers, and response handling.
    """

    def __init__(self):
        """
        Initialize the XTwitterConnection.

        Sets up the QCManager and configures the base URL for the XTwitter API.
        """
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

    @QCManager().handle_error_with_retry('twitter')
    def get_tweets(self, endpoint, query, count):
        """
        Get tweets from the XTwitter API.

        Args:
            endpoint (str): The API endpoint to request.
            query (str): The search query for tweets.
            count (int): The number of tweets to retrieve.

        Returns:
            dict: The processed response data containing the retrieved tweets.

        Raises:
            APIException: If there's an error in making the request or processing the response.
        """
        url = format_url(self.base_url, endpoint)
        data = {'query': query, 'count': count}
        response = self._make_request('POST', url, data=data)
        return self.handle_response(response)

    def handle_response(self, response):
        """
        Handle the XTwitter API response.

        Args:
            response (requests.Response): The response object from the API request.

        Returns:
            dict: The processed response data.

        Raises:
            RateLimitException: If the API rate limit is exceeded.
            AuthenticationException: If authentication fails.
            APIException: For other HTTP errors.
        """
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            self.qc_manager.log_warning(f"Rate limit exceeded. Status code: {response.status_code}", context="XTwitterConnection")
            raise RateLimitException(f"Rate limit exceeded. Status code: {response.status_code}", status_code=response.status_code)
        elif response.status_code in (401, 403):
            raise AuthenticationException("Authentication failed", status_code=response.status_code)
        else:
            raise APIException(f"HTTP error {response.status_code}: {response.text}", status_code=response.status_code)