import json
import time
from datetime import datetime, timedelta
from connections.xtwitter_connection import XTwitterConnection
from masa_tools.utils.data_storage import DataStorage
from masa_tools.qc.qc_manager import QCManager
from configs.config import settings

class XTwitterRetriever:
    def __init__(self, state_manager, request):
        """
        Initialize the XTwitterRetriever.

        :param state_manager: StateManager object for managing request states.
        :param request: Dictionary containing the request parameters.
        """
        self.qc_manager = QCManager()
        self.qc_manager.log_debug(f"Initializing XTwitterRetriever with request: {request}", context="XTwitterRetriever")
        
        if 'endpoint' not in request:
            self.qc_manager.log_error("Request does not contain 'endpoint'", context="XTwitterRetriever")
            raise ValueError("Request must contain 'endpoint'")
        
        api_endpoint = request['endpoint']
        self.qc_manager.log_debug(f"API Endpoint from request: {api_endpoint}", context="XTwitterRetriever")
        
        self.config = settings.twitter  # Get the Twitter configuration from settings
        self.qc_manager.log_debug(f"XTwitterRetriever config: {self.config}", context="XTwitterRetriever")
        full_config = {**self.config, 'api_endpoint': api_endpoint}
        
        self.qc_manager.log_debug(f"Creating XTwitterConnection with config: {full_config}", context="XTwitterRetriever")
        self.twitter_connection = XTwitterConnection(full_config)
        self.qc_manager.log_debug("XTwitterConnection created successfully", context="XTwitterRetriever")
        
        self.state_manager = state_manager
        self.qc_manager.log_debug("XTwitterRetriever initialized successfully", context="XTwitterRetriever")
        self.data_storage = DataStorage()

    @QCManager().handle_error_with_retry('twitter')
    def retrieve_tweets(self, request):
        """
        Retrieve tweets based on the given request parameters.

        :param request: Dictionary containing the request parameters. 
        :return: Tuple containing all retrieved tweets, API call count, and records fetched count.
        """
        request_id = request['id']
        self.qc_manager.log_debug(f"Starting retrieve_tweets for request {request_id}", context="XTwitterRetriever")
        return self._retrieve_tweets(request)

    def _retrieve_tweets(self, request):
        request_id = request['id']
        params = request.get('params', {})
        query = params.get('query')
        count = params.get('count')
        api_endpoint = request.get('endpoint')

        if not all([query, count, api_endpoint]):
            raise ValueError("Missing required parameters in request")

        start_date = datetime.strptime(self.config['START_DATE'], '%Y-%m-%d').date()
        end_date = datetime.strptime(self.config['END_DATE'], '%Y-%m-%d').date()
        days_per_iteration = self.config['DAYS_PER_ITERATION']

        request_state = self.state_manager.get_request_state(request_id)
        current_date = datetime.fromisoformat(request_state.get('progress', {}).get('last_processed_time', end_date.isoformat())).date()

        all_tweets = []
        api_calls_count = 0
        records_fetched = 0

        while current_date >= start_date:
            iteration_start_date = current_date - timedelta(days=days_per_iteration)
            day_before = max(iteration_start_date, start_date - timedelta(days=1))

            data = {
                'query': f"{query} since:{day_before.strftime('%Y-%m-%dT%H:%M:%SZ')} until:{current_date.strftime('%Y-%m-%dT%H:%M:%SZ')}",
                'count': count
            }
            
            response = self.twitter_connection.get_tweets(api_endpoint, query, count)
            api_calls_count += 1

            records_fetched = self._handle_response(response, request_id, query, current_date, all_tweets, records_fetched)

            current_date -= timedelta(days=days_per_iteration)
            self.state_manager.update_request_state(request_id, 'in_progress', {'last_processed_time': current_date.isoformat()})

        return all_tweets, api_calls_count, records_fetched

    def _handle_response(self, response, request_id, query, current_date, all_tweets, records_fetched):
        """
        Handle the response from the Twitter API.

        :param response: Dictionary containing the API response.
        :param request_id: ID of the request.
        :param query: Search query used for retrieving tweets.
        :param current_date: Current date being processed.
        :param all_tweets: List to store all retrieved tweets.
        :param records_fetched: Count of records fetched so far.
        """
        self.qc_manager.log_debug(f"Handling response for request {request_id}", context="XTwitterRetriever")
        
        if 'data' in response and response['data'] is not None:
            tweets = response['data']
            all_tweets.extend(tweets)
            num_tweets = len(tweets)
            records_fetched += num_tweets
            self.qc_manager.log_info(f"Fetched {num_tweets} tweets for {current_date.strftime('%Y-%m-%d')}.", context="XTwitterRetriever")
            self._save_tweets(tweets, request_id, query, current_date)
        else:
            self.qc_manager.log_warning(f"No tweets fetched for {current_date.strftime('%Y-%m-%d')}. Possibly rate limited or no results.", context="XTwitterRetriever")

        return records_fetched

    def _save_tweets(self, tweets, request_id, query, current_date):
        """
        Save the retrieved tweets and update the request state.

        :param tweets: List of retrieved tweets.
        :param request_id: ID of the request.
        :param query: Search query used for retrieving tweets.
        :param current_date: Current date being processed.
        """
        # Save tweets as JSON
        self.data_storage.save_data(tweets, 'xtwitter', query, file_format='json')
        
        self.state_manager.update_request_state(request_id, 'in_progress', {
            'last_processed_time': current_date.isoformat(),
            'tweets_count': len(tweets)
        })