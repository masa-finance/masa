"""
Module for handling connections to the XTwitter API in the MASA project.

This module provides a concrete implementation of the APIConnection class
specifically for interacting with the XTwitter API. It handles authentication,
request formatting, and response processing for XTwitter-specific endpoints.
"""

from masa_ai.connections.api_connection import APIConnection
from masa_ai.configs.config import global_settings
from masa_ai.tools.qc.qc_manager import QCManager
from masa_ai.tools.utils.helper_functions import format_url
from masa_ai.tools.qc.exceptions import AuthenticationException, APIException, RateLimitException, NoWorkersAvailableException

class XTwitterConnection(APIConnection):
    """
    masa_ai.connections.XTwitterConnection class.

    This class implements the masa_ai.connections.APIConnection interface for the masa_ai.connections.XTwitter API.
    It handles masa_ai.connections.XTwitter-specific configuration, headers, and response handling.
    """

    def __init__(self):
        """
        Initialize the XTwitterConnection.

        Sets up the QCManager and configures the base URL for the XTwitter API.
        """
        self.qc_manager = QCManager()
        self.qc_manager.log_debug("Initializing XTwitterConnection", context="XTwitterConnection")
        
        super().__init__()
        self.base_url = global_settings.get('twitter.BASE_URL') or global_settings.get('twitter.BASE_URL_LOCAL')
        self.qc_manager.log_debug(f"XTwitterConnection initialized with base URL: {self.base_url}", context="XTwitterConnection")

    def get_headers(self):
        """
        Get headers for XTwitter API requests.

        :return: A dictionary of headers to be used in the API request.
        :rtype: dict
        """
        return global_settings.get('twitter.HEADERS', {})  # Get headers from global settings

    @QCManager().handle_error_with_retry('twitter')
    def get_tweets(self, api_endpoint, date_range_query, count):
        """
        Get tweets from the XTwitter API.

        :param api_endpoint: The API endpoint to request.
        :type api_endpoint: str
        :param date_range_query: The search query for tweets.
        :type date_range_query: str
        :param count: The number of tweets to scrape.
        :type count: int
        :return: The processed response data containing the scraped tweets.
        :rtype: dict
        :raises masa_ai.tools.qc.exceptions.APIException: If there's an error in making the request or processing the response.
        """
        self.qc_manager.log_debug(f"Making API request with query: {date_range_query}, count: {count}", context="XTwitterConnection")
        url = format_url(self.base_url, api_endpoint)
        data = {'query': date_range_query, 'count': count}
        response = self._make_request('POST', url, data=data)
        result = self.handle_response(response)
        return result

    @QCManager().handle_error()
    def handle_response(self, response):
        """
        Handle the XTwitter API response.

        :param response: The response object from the API request.
        :type response: requests.Response
        :return: The processed response data.
        :rtype: dict
        :raises RateLimitException: If the API rate limit is exceeded.
        :raises AuthenticationException: If authentication fails.
        :raises masa_ai.tools.qc.exceptions.APIException: For other HTTP errors.
        """
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            raise RateLimitException("Rate limit exceeded", status_code=response.status_code)
        elif response.status_code == 417:
            raise NoWorkersAvailableException("No workers available on the network", status_code=response.status_code)
        elif response.status_code == 504:
            raise APIException("Gateway Timeout", status_code=response.status_code)
        elif response.status_code in (401, 403):
            raise AuthenticationException("Authentication failed", status_code=response.status_code)
        else:
            raise APIException(f"HTTP error {response.status_code}: {response.text}", status_code=response.status_code)
