"""
Module for retrieving tweets from the XTwitter API in the MASA project.

This module provides the XTwitterRetriever class, which handles the retrieval
of tweets from the XTwitter API, including pagination, error handling, and
data storage.
"""

import json
import time
from datetime import datetime, timedelta
from connections.xtwitter_connection import XTwitterConnection
from tools.utils.data_storage import DataStorage
from tools.qc.qc_manager import QCManager
from tools.qc.exceptions import ConfigurationException, APIException, DataProcessingException, RateLimitException
from configs.config import global_settings

class XTwitterRetriever:
    """
    XTwitter data retriever for the MASA project.

    This class handles the retrieval of tweets from the XTwitter API,
    including pagination, error handling, and data storage.
    """

    def __init__(self, state_manager, request):
        """
        Initialize the XTwitterRetriever.

        Args:
            state_manager: The state manager to track retrieval progress.
            request (dict): The request configuration for tweet retrieval.
        """
        self.qc_manager = QCManager()
        self.state_manager = state_manager
        self.request = request
        self.twitter_connection = XTwitterConnection()
        self.data_storage = DataStorage()

    def retrieve_tweets(self, request):
        """
        Retrieve tweets based on the given request.

        Args:
            request (dict): The request configuration for tweet retrieval.

        Returns:
            tuple: A tuple containing the retrieved tweets, API call count, and number of records fetched.

        Raises:
            ConfigurationException: If required parameters are missing in the request.
            APIException: If there's an error in making the API request.
            RateLimitException: If the API rate limit is exceeded.
        """
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
        """
        Handle the API response for a single request.

        This method processes the API response, extracts the tweets, and updates the retrieval statistics.

        Args:
            response (dict): The API response containing the retrieved tweets.
            request_id (str): The ID of the current request.
            query (str): The search query used for retrieving tweets.
            current_date (datetime): The current date being processed.
            all_tweets (list): The list of all tweets retrieved so far.
            records_fetched (int): The number of records fetched so far.

        Returns:
            int: The updated number of records fetched.
        """
        self.qc_manager.log_debug(f"Handling response for request {request_id}", context="XTwitterRetriever")
        
        if 'data' in response and response['data'] is not None:
            tweets = response['data']
            all_tweets.extend(tweets)
            num_tweets = len(tweets)
            records_fetched += num_tweets
            self.qc_manager.log_info(f"Scraped {num_tweets} tweets for {query} on {current_date.strftime('%Y-%m-%d %H:%M:%S')}.", context="XTwitterRetriever")
            self._save_tweets(tweets, request_id, query, current_date)
        else:
            self.qc_manager.log_warning(f"No tweets fetched for {query} on {current_date.strftime('%Y-%m-%d %H:%M:%S')}. Likely no results.", context="XTwitterRetriever")

        return records_fetched

    def _save_tweets(self, tweets, request_id, query, current_date):
        """
        Save the retrieved tweets to storage.

        This method saves the retrieved tweets to the configured data storage
        and updates the request state.

        Args:
            tweets (list): The list of tweets to save.
            request_id (str): The ID of the current request.
            query (str): The search query used for retrieving tweets.
            current_date (datetime): The current date being processed.

        Raises:
            DataProcessingException: If there's an error saving the tweets.
        """
        try:
            self.data_storage.save_data(tweets, 'xtwitter', query, file_format='json')
        except Exception as e:
            raise DataProcessingException(f"Failed to save tweets: {str(e)}")
        
        self.state_manager.update_request_state(request_id, 'in_progress', {
            'last_processed_time': current_date.isoformat(),
            'tweets_count': len(tweets)
        })