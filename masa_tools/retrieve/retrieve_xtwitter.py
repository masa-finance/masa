import json
import time
from datetime import datetime, timedelta
from connections.xtwitter_connection import XTwitterConnection
from masa_tools.utils.data_storage import DataStorage
from orchestration.retry_policy import RetryPolicy
import traceback
from masa_tools.qc.qc_manager import QCManager
from configs.config import XTwitterConfig

class XTwitterRetriever:
    def __init__(self, state_manager, request):
        """
        Initialize the XTwitterRetriever.

        :param state_manager: StateManager object for managing request states.
        :param request: Dictionary containing the request parameters.
        """
        self.qc_manager = QCManager()
        self.qc_manager.debug(f"Initializing XTwitterRetriever with request: {request}", context="XTwitterRetriever")
        
        if 'endpoint' not in request:
            self.qc_manager.debug("Request does not contain 'endpoint'", context="XTwitterRetriever")
            raise ValueError("Request must contain 'endpoint'")
        
        api_endpoint = request['endpoint']
        self.qc_manager.debug(f"API Endpoint from request: {api_endpoint}", context="XTwitterRetriever")
        
        self.config = XTwitterConfig().get_config()  # Get the Twitter configuration
        full_config = {**self.config, 'api_endpoint': api_endpoint}
        
        self.qc_manager.debug(f"Creating XTwitterConnection with config: {full_config}", context="XTwitterRetriever")
        self.twitter_connection = XTwitterConnection(full_config)
        self.qc_manager.debug("XTwitterConnection created successfully", context="XTwitterRetriever")
        
        self.state_manager = state_manager
        self.qc_manager.debug("XTwitterRetriever initialized successfully", context="XTwitterRetriever")
        self.data_storage = DataStorage()
        self.retry_policy = RetryPolicy(
            max_retries=self.config['TWITTER_MAX_RETRIES'],
            max_wait_time=self.config.get('TWITTER_RETRY_DELAY', 960),
            timeout=self.config.get('TWITTER_TIMEOUT', 30),
            success_interval=self.config.get('TWITTER_SUCCESS_INTERVAL', 7)
        )

    def retrieve_tweets(self, request):
        """
        Retrieve tweets based on the given request parameters.

        :param request: Dictionary containing the request parameters. 
        :return: Tuple containing all retrieved tweets, API call count, and records fetched count.
        """
        request_id = request['id']
        self.qc_manager.debug(f"Starting retrieve_tweets for request {request_id}", context="XTwitterRetriever")
        try:
            @self.qc_manager.handle_error_with_retry(self.retry_policy, self.config)
            def _retrieve_tweets_with_retry(request):
                request_id = request['id']
                params = request.get('params', {})
                query = params.get('query')
                count = params.get('count')
                api_endpoint = request.get('endpoint')

                if not all([query, count, api_endpoint]):
                    raise ValueError("Missing required parameters in request")

                start_date = datetime.strptime(self.config['start_time'], '%Y-%m-%dT%H:%M:%SZ').date()
                end_date = datetime.strptime(self.config['end_time'], '%Y-%m-%dT%H:%M:%SZ').date()
                days_per_iteration = 1  # Fetch tweets for 1 day at a time

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
                    
                    # The success interval wait is now handled by RetryPolicy

                return all_tweets, api_calls_count, records_fetched

            return _retrieve_tweets_with_retry(request)
        except Exception as e:
            self.qc_manager.debug(f"Error in retrieve_tweets for request {request_id}: {str(e)}", context="XTwitterRetriever")
            self.qc_manager.debug(f"Traceback: {traceback.format_exc()}", context="XTwitterRetriever")
            raise

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
        self.qc_manager.debug(f"Handling response for request {request_id}", context="XTwitterRetriever")
        
        if 'data' in response and response['data'] is not None:
            tweets = response['data']
            all_tweets.extend(tweets)
            num_tweets = len(tweets)
            records_fetched += num_tweets
            self.qc_manager.log_info(f"Fetched {num_tweets} tweets for {current_date.strftime('%Y-%m-%d')}.", context="XTwitterRetriever")
            self._save_tweets(tweets, request_id, query, current_date)
        elif 'errors' in response:
            for error in response['errors']:
                if error.get('code') == 88:  # Rate limit exceeded
                    self.qc_manager.log_warning(f"Rate limit exceeded for {current_date.strftime('%Y-%m-%d')}.", context="XTwitterRetriever")
                else:
                    self.qc_manager.log_error(f"API error: {error.get('message', 'Unknown error')}", context="XTwitterRetriever")
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
        try:
            # Save tweets as JSON
            self.data_storage.save_data(tweets, 'xtwitter', query, file_format='json')
            
            self.state_manager.update_request_state(request_id, 'in_progress', {
                'last_processed_time': current_date.isoformat(),
                'tweets_count': len(tweets)
            })
        except Exception as e:
            self.qc_manager.log_error(f"Error occurred while saving tweets or updating state: {str(e)}", context="XTwitterRetriever")
            raise