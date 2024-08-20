from masa.connections.api_connection import APIConnection
from masa.configs.config import Config

class XTwitterConnection(APIConnection):
    """
    A class for handling connections to the Twitter API.
    """

    def __init__(self):
        """
        Initialize the XTwitterConnection instance.
        """
        config = Config()
        twitter_config = config.get_twitter_config()
        
        base_url = twitter_config['api_endpoint']
        bearer_token = twitter_config['TWITTER_BEARER_TOKEN']
        headers = twitter_config['headers']
        timeout = twitter_config['request_timeout']
        max_retries = twitter_config['max_retries']
        retry_delay = twitter_config['retry_delay']
        
        super().__init__(base_url, headers, timeout, max_retries, retry_delay)
        self.bearer_token = bearer_token
        self.headers['Authorization'] = f'Bearer {bearer_token}'

    def make_request(self, endpoint, method='GET', data=None):
        """
        Make a request to the specified endpoint of the Twitter API.

        :param endpoint: The endpoint of the Twitter API. 
        :type endpoint: str
        :param method: The HTTP method to use for the request (default is 'GET').
        :type method: str
        :param data: The data to send with the request (optional).
        :type data: dict
        :return: The response from the Twitter API.
        :rtype: requests.Response
        """
        response = super().make_request(endpoint, method, data)
        self.logger.log_info(f"Request to Twitter API successful: {method} {self.base_url}/{endpoint}")
        return response