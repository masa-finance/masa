import json
import time
from datetime import datetime, timedelta
from connections.xtwitter_connection import XTwitterConnection
from masa_tools.utils.data_storage import DataStorage
from masa_tools.qc.logging import Logger
from masa_tools.qc.error_handler import ErrorHandler, GatewayTimeoutError, RequestError
from orchestration.retry_policy import RetryPolicy

class XTwitterRetriever:
    """
    A class to retrieve tweets from Twitter using the XTwitter API.

    This class is responsible for making requests to the XTwitter API to retrieve tweets
    based on given parameters. It handles error cases, retries, and saves the retrieved
    tweets to data storage.

    :param logger: A logger object for logging messages.
    :param config: A configuration object containing necessary settings.
    :param state_manager: A StateManager object for managing request states.
    """

    def __init__(self, config, state_manager):
        """
        Initialize the XTwitterRetriever.

        :param config: A configuration object containing necessary settings.
        :type config: dict
        :param state_manager: A StateManager object for managing request states.
        :type state_manager: StateManager
        """
        self.logger = Logger()
        self.config = config
        self.error_handler = ErrorHandler() 
        self.twitter_connection = XTwitterConnection()
        self.data_storage = DataStorage()
        self.state_manager = state_manager
        self.retry_policy = RetryPolicy(max_retries=3, base_wait_time=60, max_wait_time=960, gateway_timeout_wait_time=960)

    @ErrorHandler.handle_error
    def retrieve_tweets(self, request):
        """
        Retrieve tweets from Twitter based on the given request parameters.

        This method handles the main logic for retrieving tweets, including
        managing retries and updating the request state.

        :param request: A dictionary containing the request parameters.
        :type request: dict
        :raises Exception: If max retries are reached without successful retrieval.
        """
        request_id = request['id']
        params = request['params']
        query = params['query']
        count = params['count']
        start_time = datetime.strptime(self.config['start_time'], '%Y-%m-%dT%H:%M:%SZ')
        end_time = datetime.strptime(self.config['end_time'], '%Y-%m-%dT%H:%M:%SZ')
        days_per_iteration = self.config.get('days_per_iteration', 1)

        request_state = self.state_manager.get_request_state(request_id)
        current_time = datetime.fromisoformat(request_state.get('progress', {}).get('last_processed_time', end_time.isoformat()))

        retry_count = 0
        while retry_count < self.retry_policy.max_retries:
            try:
                while current_time >= start_time:
                    data = {
                        'query': f"{query} since:{(current_time - timedelta(days=days_per_iteration)).strftime('%Y-%m-%dT%H:%M:%SZ')} until:{current_time.strftime('%Y-%m-%dT%H:%M:%SZ')}",
                        'count': count
                    }
                    response = self.twitter_connection.make_request('/data/twitter/tweets/recent', method='POST', data=data)
                    self._handle_response(response, request_id, query, current_time)

                    current_time -= timedelta(days=days_per_iteration)
                    self.state_manager.update_request_state(request_id, 'in_progress', {'last_processed_time': current_time.isoformat()})
                    time.sleep(self.config.get('request_delay', 15))

                break  # If successful, break the retry loop

            except GatewayTimeoutError as e:
                retry_count += 1
                wait_time = self.retry_policy.gateway_timeout_wait_time
                self.logger.log_warning(f"Gateway Timeout error retrieving tweets for request {request_id}. Retrying in {wait_time} seconds. Error: {str(e)}")
                self.state_manager.update_request_state(request_id, 'retrying', progress={'error': str(e), 'retry_count': retry_count})
                time.sleep(wait_time)
            except RequestError as e:
                retry_count += 1
                wait_time = self.retry_policy.wait_time(retry_count)
                self.logger.log_warning(f"Error retrieving tweets for request {request_id}. Retrying in {wait_time} seconds. Error: {str(e)}")
                self.state_manager.update_request_state(request_id, 'retrying', progress={'error': str(e), 'retry_count': retry_count})
                time.sleep(wait_time)

        if retry_count == self.retry_policy.max_retries:
            self.logger.log_error(f"Max retries reached for request {request_id}")
            raise Exception("Max retries reached")

    def _handle_response(self, response, request_id, query, current_time):
        """
        Handle the response from the XTwitter API.

        This method processes the API response, saves the tweets if successful,
        and raises appropriate errors if not.

        :param response: The response object from the XTwitter API.
        :type response: requests.Response
        :param request_id: The ID of the request.
        :type request_id: str
        :param query: The query used for the request.
        :type query: str
        :param current_time: The current time for the request.
        :type current_time: datetime
        :raises MissingDataError: If the 'data' key is missing in the response.
        :raises RequestError: If the request failed (non-200 status code).
        """
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                tweets = data['data']
                self._save_tweets(tweets, request_id, query, current_time)
                self.logger.log_info(f"Successfully retrieved and saved {len(tweets)} tweets for {query} at {current_time}")
            else:
                self.error_handler.raise_error("MissingDataError", "The 'data' key is missing in the response.")
        else:
            self.error_handler.raise_error("RequestError", f"Failed to retrieve tweets. Status code: {response.status_code}")

    def _save_tweets(self, tweets, request_id, query, current_time):
        """
        Save the retrieved tweets to the data storage.

        This method saves the tweets and updates the request state.

        :param tweets: A list of tweet objects.
        :type tweets: list
        :param request_id: The ID of the request.
        :type request_id: str
        :param query: The query used for the request.
        :type query: str
        :param current_time: The current time for the request.
        :type current_time: datetime
        """
        try:
            tweets_json = json.dumps(tweets)
            self.data_storage.save_data(tweets_json, 'xtwitter', query)
            self.state_manager.update_request_state(request_id, 'in_progress', {
                'last_processed_time': current_time.isoformat(),
                'tweets_count': len(tweets)
            })
        except Exception as e:
            self.logger.log_error(f"Error occurred while saving tweets or updating state: {str(e)}")
            raise