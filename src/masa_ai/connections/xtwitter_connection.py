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
from masa_ai.tools.qc.exceptions import (
    AuthenticationException,
    APIException,
    RateLimitException,
    NoWorkersAvailableException,
)

class XTwitterConnection(APIConnection):
    """
    Class for handling connections to the XTwitter API.

    Implements the APIConnection interface specifically for XTwitter.
    """

    def __init__(self):
        """
        Initialize the XTwitterConnection.

        Sets up the QCManager and configures the base URL for the XTwitter API.
        """
        super().__init__()
        self.qc_manager.log_debug("Initializing XTwitterConnection", context="XTwitterConnection")
        self.base_url = global_settings.get('twitter.BASE_URL') or global_settings.get('twitter.BASE_URL_LOCAL')
        self.qc_manager.log_debug(f"XTwitterConnection initialized with base URL: {self.base_url}", context="XTwitterConnection")

    def get_headers(self):
        """
        Get headers for XTwitter API requests.

        Returns:
            dict: A dictionary of headers.
        """
        return global_settings.get('twitter.HEADERS', {})

    @QCManager().handle_error_with_retry('twitter')
    def get_tweets(self, api_endpoint, date_range_query, count):
        """
        Get tweets from the XTwitter API.

        Args:
            api_endpoint (str): The API endpoint to request.
            date_range_query (str): The search query for tweets.
            count (int): The number of tweets to scrape.

        Returns:
            dict: The processed response data containing the scraped tweets.

        Raises:
            APIException: If there's an error in making the request or processing the response.
        """
        self.qc_manager.log_debug(
            f"Making API request with query: {date_range_query}, count: {count}",
            context="XTwitterConnection"
        )
        url = format_url(self.base_url, api_endpoint)
        data = {'query': date_range_query, 'count': count}
        response = self._make_request('POST', url, data=data)
        result = self.handle_response(response)
        return result

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
            raise RateLimitException("Rate limit exceeded", status_code=response.status_code)
        elif response.status_code == 417:
            raise NoWorkersAvailableException(
                "No workers available on the network",
                status_code=response.status_code
            )
        elif response.status_code == 504:
            raise APIException("Gateway Timeout", status_code=response.status_code)
        elif response.status_code in (401, 403):
            raise AuthenticationException("Authentication failed", status_code=response.status_code)
        else:
            raise APIException(
                f"HTTP error {response.status_code}: {response.text}",
                status_code=response.status_code
            )
