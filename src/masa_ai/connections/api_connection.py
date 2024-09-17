"""
Module for handling generic API connections in the MASA project.

This module provides an abstract base class for API connections, defining
the interface for making API requests and handling responses. It includes
error handling and logging functionality using the QCManager.
"""

import requests
from abc import ABC, abstractmethod
from masa_ai.configs.config import global_settings
from masa_ai.tools.qc.qc_manager import QCManager
from masa_ai.tools.qc.exceptions import APIException, NetworkException, ConfigurationException, RateLimitException

class APIConnection(ABC):
    """
    Abstract base class for API connections.

    This class defines the interface for making API requests and handling responses.
    Subclasses should implement the abstract methods to provide specific behavior
    for different APIs.

    Attributes:
        base_url (str): The base URL for the API.
        qc_manager (tools.qc.qc_manager.QCManager): Quality control manager for logging and error handling.
    """

    def __init__(self):
        """
        Initialize the APIConnection.

        Raises:
            ConfigurationException: If neither BASE_URL nor BASE_URL_LOCAL is set in the configuration.
        """
        self.qc_manager = QCManager()
        base_url = global_settings.get('twitter.BASE_URL') or global_settings.get('twitter.BASE_URL_LOCAL')
        self.qc_manager.log_debug(f"Initializing APIConnection with base_url: {base_url}", context="APIConnection")
        if not base_url:
            raise ConfigurationException("Neither BASE_URL nor BASE_URL_LOCAL is set in the configuration")
        self.base_url = base_url.rstrip('/')

    @abstractmethod
    def get_headers(self):
        """
        Return headers for the API request.

        This method should be implemented by subclasses to provide
        API-specific headers.

        Returns:
            dict: A dictionary of headers to be used in the API request.
        """
        pass

    @abstractmethod
    def handle_response(self, response):
        """
        Handle the API response.

        This method should be implemented by subclasses to provide
        API-specific response handling.

        Args:
            response (requests.Response): The response object from the API request.

        Returns:
            dict: The processed response data.

        Raises:
            APIException: If there's an error in processing the response.
        """
        pass

    @QCManager().handle_error_with_retry('twitter')
    def _make_request(self, method, url, data=None, params=None):
        """
        Make an API request.

        Args:
            method (str): The HTTP method for the request (e.g., 'GET', 'POST').
            url (str): The full URL for the API request.
            data (dict, optional): The data to send in the request body.
            params (dict, optional): The query parameters for the request.

        Returns:
            requests.Response: The raw response object.

        Raises:
            NetworkException: If there's a network-related error.
            APIException: If there's an error in making the request or processing the response.
            RateLimitException: If the API rate limit is exceeded (status code 429).
        """
        headers = self.get_headers()
        try:
            response = requests.request(
                method, 
                url, 
                json=data,
                params=params,
                headers=headers
            )
            if response.status_code == 429:
                raise RateLimitException(f"Rate limit exceeded. Status code: {response.status_code}", status_code=response.status_code)
            response.raise_for_status()
            return response
        except requests.exceptions.ConnectionError as e:
            raise NetworkException(f"Connection error: {str(e)}")
        except requests.exceptions.Timeout as e:
            raise NetworkException(f"Request timed out: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise APIException(f"Request failed: {str(e)}")