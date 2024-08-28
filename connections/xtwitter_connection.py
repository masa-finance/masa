from .api_connection import APIConnection
from masa_tools.qc.qc_manager import QCManager
from orchestration.retry_policy import RetryPolicy

class XTwitterConnection(APIConnection):
    """
    XTwitter API connection class.

    This class implements the APIConnection interface for the XTwitter API.
    It handles XTwitter-specific configuration, headers, timeouts, and response handling.

    Attributes:
        config (dict): Configuration dictionary for the XTwitter API.
        retry_policy (RetryPolicy): Retry policy for handling request failures.
    """

    def __init__(self, config):
        """
        Initialize the XTwitterConnection.

        Args:
            config (dict): Configuration dictionary for the XTwitter API.
        """
        self.qc_manager = QCManager()
        self.qc_manager.log_debug(f"XTwitterConnection received config: {config}", context="XTwitterConnection")
        base_url = config.get('BASE_URL')
        self.qc_manager.log_debug(f"BASE_URL from config: {base_url}", context="XTwitterConnection")
        self.qc_manager.log_debug(f"Initializing XTwitterConnection with config: {config}", context="XTwitterConnection")
        
        if not base_url:
            self.qc_manager.log_debug("Base URL is None or empty", context="XTwitterConnection")
            raise ValueError("Base URL cannot be None or empty")
        
        super().__init__(base_url=base_url)
        self.qc_manager.log_debug("XTwitterConnection initialized successfully", context="XTwitterConnection")
        self.config = config
        self.retry_policy = RetryPolicy(
            max_retries=config.get('TWITTER_MAX_RETRIES', 3),
            base_wait_time=config.get('TWITTER_RETRY_DELAY', 960),
            max_wait_time=config.get('TWITTER_RETRY_DELAY', 960),
            timeout=config.get('TWITTER_TIMEOUT', 30),
            success_interval=config.get('TWITTER_SUCCESS_INTERVAL', 7)
        )
        self.current_wait_time = self.retry_policy.base_wait_time
        self.consecutive_504_count = 0

    def get_headers(self):
        """
        Get headers for XTwitter API requests.

        Returns:
            dict: A dictionary of headers to be used in the API request.
        """
        return {
            **self.config.get('headers', {}),
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def get_timeout(self):
        """
        Get timeout for XTwitter API requests.

        Returns:
            int: The timeout value in seconds for the API request.
        """
        return self.config.get('request_timeout', 30)

    def handle_response(self, response):
        """
        Handle the XTwitter API response.

        Args:
            response (requests.Response): The response object from the API request.

        Returns:
            dict: The processed response data.

        Raises:
            Exception: For various HTTP errors, to be handled by QCManager.
        """
        if response.status_code == 200:
            self.consecutive_504_count = 0
            self.current_wait_time = self.retry_policy.base_wait_time
            return response.json()
        elif response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', self.retry_policy.max_wait_time))
            raise RateLimitError(retry_after)
        elif response.status_code == 504:
            self.consecutive_504_count += 1
            self.current_wait_time = min(self.current_wait_time * 2, self.retry_policy.max_wait_time)
            raise GatewayTimeoutError(self.current_wait_time)
        elif response.status_code >= 500:
            raise ServerError(response.status_code)
        else:
            response.raise_for_status()

    def make_request(self, endpoint, method='POST', data=None):
        """
        Make a request to the XTwitter API.

        This method is decorated with error handling and retry logic.

        Args:
            endpoint (str): The API endpoint to request.
            method (str, optional): The HTTP method for the request. Defaults to 'POST'.
            data (dict, optional): The data to send in the request body.

        Returns:
            requests.Response: The raw response object from the API request.
        """
        @self.qc_manager.handle_error_with_retry(self.retry_policy, self.config)
        def _make_request_with_retry():
            return self._make_request(method, endpoint, data=data)

        return _make_request_with_retry()

    def get_tweets(self, endpoint, query, count):
        """
        Get tweets from the XTwitter API.

        Args:
            endpoint (str): The API endpoint to request.
            query (str): The search query for tweets.
            count (int): The number of tweets to retrieve.

        Returns:
            requests.Response: The raw response object from the API request.
        """
        data = {'query': query, 'count': count}
        return self.make_request(endpoint, method='POST', data=data)