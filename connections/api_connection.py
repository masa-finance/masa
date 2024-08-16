import requests
from masa.qc.logging import Logger
from masa.qc.error_handler import ErrorHandler

class APIConnection:
    """
    A class for handling API connections and requests.
    """

    def __init__(self, base_url):
        """
        Initialize the APIConnection instance.

        :param base_url: The base URL of the API.
        :type base_url: str
        """
        self.base_url = base_url
        self.logger = Logger("APIConnection")
        self.error_handler = ErrorHandler(self.logger)

    @ErrorHandler.handle_error
    def make_request(self, endpoint, method='GET', data=None):
        """
        Make an API request to the specified endpoint.

        :param endpoint: The endpoint of the API.
        :type endpoint: str
        :param method: The HTTP method to use for the request (default is 'GET').
        :type method: str
        :param data: The data to send with the request (optional).
        :type data: dict
        :return: The response from the API.
        :rtype: requests.Response
        """
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.request(method, url, json=data)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            self.logger.log_info(f"API request successful: {method} {url}")
            return response
        except requests.exceptions.RequestException as e:
            self.error_handler.raise_error("RequestException", str(e))

    def get(self, endpoint, params=None):
        """
        Make a GET request to the specified endpoint.

        :param endpoint: The endpoint of the API.
        :type endpoint: str
        :param params: The query parameters to include in the request (optional).
        :type params: dict
        :return: The response from the API.
        :rtype: requests.Response
        """
        return self.make_request(endpoint, method='GET', data=params)

    def post(self, endpoint, data):
        """
        Make a POST request to the specified endpoint.

        :param endpoint: The endpoint of the API.
        :type endpoint: str
        :param data: The data to send with the request.
        :type data: dict
        :return: The response from the API.
        :rtype: requests.Response
        """
        return self.make_request(endpoint, method='POST', data=data)