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

        Args:
            base_url (str): The base URL for the API.
        """
        self.qc_manager = QCManager()
        self.qc_manager.debug(f"Initializing APIConnection with base_url: {base_url}", context="APIConnection")
        if not base_url:
            raise ValueError("base_url cannot be None or empty")
        self.base_url = base_url.rstrip('/')
        self.qc_manager = QCManager()

    @abstractmethod
    def get_headers(self):
        """
        Return headers for the API request.

        Returns:
            dict: A dictionary of headers to be used in the API request.
        """
        pass

    @abstractmethod
    def get_timeout(self):
        """
        Return timeout for the API request.

        Returns:
            int: The timeout value in seconds for the API request.
        """
        pass

    @abstractmethod
    def handle_response(self, response):
        """
        Handle the API response.

        Args:
            response (requests.Response): The response object from the API request.

        Returns:
            dict: The processed response data.

        Raises:
            Exception: If there's an error in processing the response.
        """
        pass

    def _make_request(self, method, endpoint, data=None, params=None):
        """
        Make an API request.

        Args:
            method (str): The HTTP method for the request (e.g., 'GET', 'POST').
            endpoint (str): The API endpoint to request.
            data (dict, optional): The data to send in the request body.
            params (dict, optional): The query parameters for the request.

        Returns:
            dict: The processed response data.

        Raises:
            requests.RequestException: If there's an error in making the request.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self.get_headers()
        timeout = self.get_timeout()

        try:
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
            self.qc_manager.log_error(f"API request failed: {str(e)}", context=self.__class__.__name__)
            raise