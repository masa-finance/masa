import json
import time
from datetime import datetime, timedelta
from connections.xtwitter_connection import XTwitterConnection
from masa_tools.utils.data_storage import DataStorage
from masa_tools.qc.error_handler import ErrorHandler

class XTwitterRetriever:
    """
    A class to retrieve tweets from Twitter using the XTwitter API.

    This class is responsible for making requests to the XTwitter API to retrieve tweets
    based on a given query and count. It also handles error cases and saves the retrieved
    tweets to a data storage.

    :param logger: A logger object for logging messages.
    :param config: A configuration object containing necessary settings.
    :param state_manager: A StateManager object for managing request states.
    """

    def __init__(self, logger, config, state_manager):
        """
        Initialize the XTwitterRetriever.

        :param logger: A logger object for logging messages.
        :param config: A configuration object containing necessary settings.
        :param state_manager: A StateManager object for managing request states.
        """
        self.logger = logger
        self.config = config
        self.error_handler = ErrorHandler(self.logger)
        self.twitter_connection = XTwitterConnection()
        self.data_storage = DataStorage()
        self.state_manager = state_manager

    @ErrorHandler.handle_error
    def retrieve_tweets(self, request):
        """
        Retrieve tweets from Twitter based on the given request parameters.

        :param request: A dictionary containing the request parameters.
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

        while current_time >= start_time:
            success = False
            attempts = 0
            while not success and attempts < self.config.get('max_retries', 3):
                iteration_start_time = current_time - timedelta(days=days_per_iteration)
                day_before = max(iteration_start_time, start_time - timedelta(days=1))

                data = {
                    'query': f"{query} since:{day_before.strftime('%Y-%m-%dT%H:%M:%SZ')} until:{current_time.strftime('%Y-%m-%dT%H:%M:%SZ')}",
                    'count': count
                }
                response = self.twitter_connection.make_request('/data/twitter/tweets/recent', method='POST', data=data)
                success = self._handle_response(response, request_id, query, current_time)

                if not success:
                    self.logger.log_warning(f"Request failed for {current_time} to {day_before}. Retrying in {self.config.get('retry_delay', 60)} seconds...")
                    time.sleep(self.config.get('retry_delay', 60))
                    attempts += 1

            if not success:
                self.error_handler.raise_error("RetrievalError", f"Failed to process request for {current_time} to {day_before} after {attempts} attempts.")

            current_time -= timedelta(days=days_per_iteration)
            self.state_manager.update_request_state(request_id, 'in_progress', {'last_processed_time': current_time.isoformat()})
            time.sleep(self.config.get('request_delay', 15))

    @ErrorHandler.handle_error
    def _handle_response(self, response, request_id, query, current_time):
        """
        Handle the response from the XTwitter API.

        :param response: The response object from the XTwitter API.
        :param request_id: The ID of the request.
        :param query: The query used for the request.
        :param current_time: The current time for the request.
        :return: True if the response was successful, False otherwise.
        """
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                tweets = data['data']
                self._save_tweets(tweets, request_id, query, current_time)
                self.logger.log_info(f"Successfully retrieved and saved {len(tweets)} tweets for {query} at {current_time}")
                return True
            else:
                self.error_handler.raise_error("MissingDataError", "The 'data' key is missing in the response.")
        else:
            self.error_handler.raise_error("RequestError", f"Failed to retrieve tweets. Status code: {response.status_code}")
        return False

    def _save_tweets(self, tweets, request_id, query, current_time):
        """
        Save the retrieved tweets to the data storage.

        :param tweets: A list of tweet objects.
        :param request_id: The ID of the request.
        :param query: The query used for the request.
        :param current_time: The current time for the request.
        """
        tweets_json = json.dumps(tweets)
        self.data_storage.save_data(tweets_json, 'xtwitter', query)
        self.state_manager.update_request_state(request_id, 'in_progress', {
            'last_processed_time': current_time.isoformat(),
            'tweets_count': len(tweets)
        })