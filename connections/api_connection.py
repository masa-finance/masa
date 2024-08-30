import requests
from abc import ABC, abstractmethod
from configs.config import global_settings
from masa_tools.qc.qc_manager import QCManager
from masa_tools.qc.exceptions import APIException, NetworkException, ConfigurationException, RateLimitException

class APIConnection(ABC):
    """
    Abstract base class for API connections.

    This class defines the interface for making API requests and handling responses.
    Subclasses should implement the abstract methods to provide specific behavior
    for different APIs.

    Attributes:
        base_url (str): The base URL for the API.
        qc_manager (QCManager): Quality control manager for logging and error handling.
    """

    def __init__(self):
        """
        Initialize the APIConnection.
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

        :return: A dictionary of headers to be used in the API request.
        :rtype: dict
        """
        pass

    @abstractmethod
    def handle_response(self, response):
        """
        Handle the API response.

        :param response: The response object from the API request.
        :type response: requests.Response
        :return: The processed response data.
        :rtype: dict
        :raises APIException: If there's an error in processing the response.
        """
        pass

    def _make_request(self, method, url, data=None, params=None):
        """
        Make an API request.

        :param method: The HTTP method for the request (e.g., 'GET', 'POST').
        :type method: str
        :param endpoint: The API endpoint to request.
        :type endpoint: str
        :param data: The data to send in the request body.
        :type data: dict, optional
        :param params: The query parameters for the request.
        :type params: dict, optional
        :return: The raw response object.
        :rtype: requests.Response
        :raises APIException: If there's an error in making the request or processing the response.
        :raises RateLimitException: If the API rate limit is exceeded (status code 429).
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