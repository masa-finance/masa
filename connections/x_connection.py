from masa.connections.api_connection import APIConnection

class XConnection(APIConnection):
    """
    A class for handling connections to the X service or API.
    """

    def __init__(self, base_url, api_key, headers=None, timeout=30, max_retries=3, retry_delay=960):
        """
        Initialize the XConnection instance.

        :param base_url: The base URL of the X service or API.
        :type base_url: str
        :param api_key: The API key for authentication.
        :type api_key: str
        :param headers: The headers to include in the requests (optional).
        :type headers: dict
        :param timeout: The request timeout in seconds (default is 30).
        :type timeout: int
        :param max_retries: The maximum number of retries for failed requests (default is 3).
        :type max_retries: int
        :param retry_delay: The delay in seconds between retries (default is 960).
        :type retry_delay: int
        """
        super().__init__(base_url, headers, timeout, max_retries, retry_delay)
        self.api_key = api_key
        self.headers['X-API-Key'] = api_key

    def make_request(self, endpoint, method='GET', data=None):
        """
        Make a request to the specified endpoint of the X service or API.

        :param endpoint: The endpoint of the X service or API.
        :type endpoint: str
        :param method: The HTTP method to use for the request (default is 'GET').
        :type method: str
        :param data: The data to send with the request (optional).
        :type data: dict
        :return: The response from the X service or API.
        :rtype: requests.Response
        """
        response = super().make_request(endpoint, method, data)
        self.logger.log_info(f"Request to X service or API successful: {method} {self.base_url}/{endpoint}")
        return response