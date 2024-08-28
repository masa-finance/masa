import requests
from abc import ABC, abstractmethod
from masa_tools.qc.qc_manager import QCManager

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

    def __init__(self, base_url):
        """
        Initialize the APIConnection.

        :param base_url: The base URL for the API.
        :type base_url: str
        """
        self.qc_manager = QCManager()
        self.qc_manager.debug(f"Initializing APIConnection with base_url: {base_url}", context="APIConnection")
        if not base_url:
            raise ValueError("base_url cannot be None or empty")
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
    def get_timeout(self):
        """
        Return timeout for the API request.

        :return: The timeout value in seconds for the API request.
        :rtype: int
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
        :raises Exception: If there's an error in processing the response.
        """
        pass

    def _make_request(self, method, endpoint, data=None, params=None):
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
        :return: The processed response data.
        :rtype: dict
        :raises requests.RequestException: If there's an error in making the request.
        """
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            headers = self.get_headers()
            timeout = self.get_timeout()

            response = requests.request(
                method, 
                url, 
                json=data,
                params=params,
                headers=headers, 
                timeout=timeout
            )
            return self.handle_response(response)
        except requests.RequestException as e:
            self.qc_manager.log_error(f"API request failed: {str(e)}", error_info=e, context=self.__class__.__name__)
            raise