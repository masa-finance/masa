"""
Module for retrieving tweets from the XTwitter API in the MASA project.

This module provides the XTwitterRetriever class, which handles the retrieval
of tweets from the XTwitter API, including pagination, error handling, and
data storage.
"""

import json
import time
from datetime import datetime, timedelta
import re
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
        self.qc_manager.log_debug(f"Request object: {request}", context="XTwitterRetriever")
        request_id = request.get('request_id')
        params = request.get('params', {})
        query = params.get('query')
        count = params.get('count')
        api_endpoint = request.get('endpoint')

        self.qc_manager.log_debug(f"Query: {query}", context="XTwitterRetriever")

        if not all([query, count, api_endpoint]):
            raise ConfigurationException("Missing required parameters in request")

        # Extract time-related parameters
        start_date, end_date, cleaned_query = self._extract_date_range(query)
        
        # Use default timeframe if not provided in the query
        if not end_date:
            end_date = datetime.now().date()
        if not start_date:
            default_months = global_settings.get('twitter.DEFAULT_TIMEFRAME_MONTHS', 3)
            start_date = end_date - timedelta(days=30 * default_months)

        days_per_iteration = global_settings.get('twitter.DAYS_PER_ITERATION', 1)

        request_state = self.state_manager.get_request_state(request_id)
        current_date = datetime.fromisoformat(request_state.get('progress', {}).get('last_processed_time', end_date.isoformat())).date()

        total_days = (end_date - start_date).days
        self.qc_manager.log_info(f"Starting tweet retrieval for query: {query} over {total_days} days", context="XTwitterRetriever")

        all_tweets = []
        api_calls_count = 0
        records_fetched = 0
        days_processed = 0

        while current_date >= start_date:
            iteration_start_date = current_date - timedelta(days=days_per_iteration)
            day_before = max(iteration_start_date, start_date - timedelta(days=1))

            date_range_query = f"{cleaned_query} since:{day_before.strftime('%Y-%m-%dT%H:%M:%SZ')} until:{current_date.strftime('%Y-%m-%dT%H:%M:%SZ')}"
            
            response = self.twitter_connection.get_tweets(api_endpoint, date_range_query, count)
            api_calls_count += 1
            new_records = self._handle_response(response, request_id, query, current_date, all_tweets, records_fetched)
            records_fetched += new_records

            days_processed += days_per_iteration
            progress_percentage = min(100, int((days_processed / total_days) * 100))
            self.qc_manager.log_info(f"Tweet retrieval progress: {progress_percentage}% ({records_fetched} tweets fetched)", context="XTwitterRetriever")

            current_date -= timedelta(days=days_per_iteration)
            self.state_manager.update_request_state(request_id, 'in_progress', {'last_processed_time': current_date.isoformat()})

        self.qc_manager.log_info(f"Tweet retrieval completed for query: {query} over {total_days} days. Total tweets: {records_fetched}, API calls: {api_calls_count}", context="XTwitterRetriever")
        return all_tweets, api_calls_count, records_fetched

    def _handle_response(self, response, request_id, query, current_date, all_tweets, records_fetched):
        if 'data' in response and response['data'] is not None:
            tweets = response['data']
            all_tweets.extend(tweets)
            num_tweets = len(tweets)
            self._save_tweets(tweets, request_id, query, current_date)
            self.qc_manager.log_debug(f"Scraped and saved {num_tweets} tweets for {query} on {current_date.strftime('%Y-%m-%d')}.", context="XTwitterRetriever")
            return num_tweets
        else:
            self.qc_manager.log_debug(f"No tweets fetched for {query} on {current_date.strftime('%Y-%m-%d')}. Likely no results.", context="XTwitterRetriever")
            return 0

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

    def _extract_date_range(self, query):
        self.qc_manager.log_debug(f"Query: {query}", context="XTwitterRetriever")
        start_date = None
        end_date = None
        
        # Extract 'since' date
        since_match = re.search(r'since:(\d{4}-\d{2}-\d{2})', query)
        if since_match:
            start_date = datetime.strptime(since_match.group(1), '%Y-%m-%d').date()
            query = query.replace(since_match.group(0), '').strip()

        # Extract 'until' date
        until_match = re.search(r'until:(\d{4}-\d{2}-\d{2})', query)
        if until_match:
            end_date = datetime.strptime(until_match.group(1), '%Y-%m-%d').date()
            query = query.replace(until_match.group(0), '').strip()

        self.qc_manager.log_debug(f"Start date: {start_date}, End date: {end_date}", context="XTwitterRetriever")
        return start_date, end_date, query