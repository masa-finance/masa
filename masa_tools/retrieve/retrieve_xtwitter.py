import json
import time
from datetime import datetime, timedelta
from connections.xtwitter_connection import XTwitterConnection
from masa_tools.utils.data_storage import DataStorage
from masa_tools.qc.qc_manager import QCManager
from configs.config import global_settings
from masa_tools.qc.exceptions import ConfigurationException, APIException, DataProcessingException

class XTwitterRetriever:
    def __init__(self, state_manager, request):
        self.qc_manager = QCManager()
        self.state_manager = state_manager
        self.request = request
        self.api_endpoint = request.get('endpoint')
        self.twitter_connection = XTwitterConnection()
        self.data_storage = DataStorage()

    @QCManager().handle_error_with_retry('twitter')
    def retrieve_tweets(self, request):
        request_id = request['id']
        request_params = request.get('params', {})
        query = request_params.get('query')
        self.qc_manager.log_debug(f"Starting retrieve_tweets for request {query} (ID: {request_id})", context="XTwitterRetriever")
        self.qc_manager.log_info(f"Starting retrieve_tweets for request {query} (ID: {request_id})", context="XTwitterRetriever")
        return self._retrieve_tweets(request)

    def _retrieve_tweets(self, request):
        request_id = request['id']
        params = request.get('params', {})
        query = params.get('query')
        count = params.get('count')
        api_endpoint = request.get('endpoint')

        if not all([query, count, api_endpoint]):
            raise ConfigurationException("Missing required parameters in request")

        start_date = datetime.strptime(global_settings.get('twitter.START_DATE'), '%Y-%m-%d').date()
        end_date = datetime.strptime(global_settings.get('twitter.END_DATE'), '%Y-%m-%d').date()
        days_per_iteration = global_settings.get('twitter.DAYS_PER_ITERATION', 1)

        request_state = self.state_manager.get_request_state(request_id)
        current_date = datetime.fromisoformat(request_state.get('progress', {}).get('last_processed_time', end_date.isoformat())).date()

        all_tweets = []
        api_calls_count = 0
        records_fetched = 0

        while current_date >= start_date:
            iteration_start_date = current_date - timedelta(days=days_per_iteration)
            day_before = max(iteration_start_date, start_date - timedelta(days=1))

            date_range_query = f"{query} since:{day_before.strftime('%Y-%m-%dT%H:%M:%SZ')} until:{current_date.strftime('%Y-%m-%dT%H:%M:%SZ')}"
            
            response = self.twitter_connection.get_tweets(api_endpoint, date_range_query, count)
            api_calls_count += 1
            records_fetched = self._handle_response(response, request_id, query, current_date, all_tweets, records_fetched)

            current_date -= timedelta(days=days_per_iteration)
            self.state_manager.update_request_state(request_id, 'in_progress', {'last_processed_time': current_date.isoformat()})

        return all_tweets, api_calls_count, records_fetched

    def _handle_response(self, response, request_id, query, current_date, all_tweets, records_fetched):
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
        try:
            self.data_storage.save_data(tweets, 'xtwitter', query, file_format='json')
        except Exception as e:
            raise DataProcessingException(f"Failed to save tweets: {str(e)}")
        
        self.state_manager.update_request_state(request_id, 'in_progress', {
            'last_processed_time': current_date.isoformat(),
            'tweets_count': len(tweets)
        })