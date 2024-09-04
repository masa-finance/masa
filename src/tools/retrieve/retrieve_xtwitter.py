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

    @QCManager().handle_error()
    def retrieve_tweets(self, request_id, query, count):
        """
        Retrieve tweets based on the given request.

        Args:
            request_id (str): The ID of the request.
            query (str): The search query for tweets.
            count (int): The number of tweets to retrieve per API call.

        Returns:
            tuple: A tuple containing the retrieved tweets, API call count, and number of records fetched.

        Raises:
            ConfigurationException: If required parameters are missing in the request.
            APIException: If there's an error in making the API request.
            RateLimitException: If the API rate limit is exceeded.
        """
        self.qc_manager.log_debug(f"Starting retrieve_tweets for request: {request_id}", context="XTwitterRetriever")
        request = self.state_manager.get_request_state(request_id)
        params = request.get('params', {})
        api_endpoint = self.request.get('endpoint')
        

        self.qc_manager.log_debug(f"Query: {query}, Count: {count} for {api_endpoint}", context="XTwitterRetriever")

        if not all([query, count, api_endpoint]):
            raise ConfigurationException("Missing required parameters in request")

        # Extract time-related parameters
        start_date, end_date, cleaned_query = self._extract_date_range(query)
        
        self.qc_manager.log_debug(f"Extracted date range: {start_date} to {end_date}", context="XTwitterRetriever")
        
        # Get the default timeframe from settings
        default_months = global_settings.get('twitter.DEFAULT_TIMEFRAME_MONTHS', 3)
        
        # Apply the logic for date range
        current_date = datetime.now().date()
        if not end_date:
            end_date = current_date
        if not start_date:
            start_date = end_date - timedelta(days=30 * default_months)

        days_per_iteration = global_settings.get('twitter.DAYS_PER_ITERATION', 1)

        request_state = self.state_manager.get_request_state(request_id)
        
        # Initialize current_date to end_date or the last processed time
        current_date = datetime.fromisoformat(
            request_state.get('progress', {}).get('last_processed_time', end_date.isoformat())
        ).date()

        # Ensure current_date is not later than end_date
        current_date = min(current_date, end_date)

        total_days = (end_date - start_date).days
        self.qc_manager.log_info(f"Starting tweet retrieval for query: {query} over {total_days} days", context="XTwitterRetriever")

        all_tweets = []
        api_calls_count = 0
        records_fetched = 0
        days_processed = 0

        while current_date >= start_date:
            self.qc_manager.log_debug(f"Processing date: {current_date}", context="XTwitterRetriever")
            iteration_end_date = current_date
            iteration_start_date = current_date

            # For the query, we need to use the day after current_date as the "until" date
            query_until_date = (iteration_end_date + timedelta(days=1)).strftime('%Y-%m-%d')
            date_range_query = f"{cleaned_query} since:{iteration_start_date.strftime('%Y-%m-%d')} until:{query_until_date}"
            
            self.qc_manager.log_debug(f"Processing date: {iteration_start_date}", context="XTwitterRetriever")
            
            self.qc_manager.log_debug(f"Calling twitter_connection.get_tweets with query: {date_range_query}, count: {count}, start_time: {current_date}, end_time: {current_date + timedelta(days=1)}", context="XTwitterRetriever")
            try:
                response = self.twitter_connection.get_tweets(api_endpoint, date_range_query, count)
                self.qc_manager.log_debug(f"Received response from API", context="XTwitterRetriever")
            except Exception as e:
                self.qc_manager.log_error(f"API call failed: {str(e)}", context="XTwitterRetriever")
            
            api_calls_count += 1
            new_records = self._handle_response(response, request_id, query, iteration_end_date, all_tweets, records_fetched)
            records_fetched += new_records
            self.qc_manager.log_debug(f"Received {new_records} tweets from API, total records fetched: {records_fetched}", context="XTwitterRetriever")

            days_processed += 1
            progress_percentage = min(100, int((days_processed / total_days) * 100))
            self.qc_manager.log_info(f"Tweet retrieval progress: {progress_percentage}% ({records_fetched} tweets fetched)", context="XTwitterRetriever")

            current_date -= timedelta(days=1)
            self.state_manager.update_request_state(request_id, 'in_progress', {'last_processed_time': current_date.isoformat()})

        self.qc_manager.log_info(f"Tweet retrieval completed for query: {query} over {total_days} days. Total tweets: {records_fetched}, API calls: {api_calls_count}", context="XTwitterRetriever")
        return all_tweets, api_calls_count, records_fetched

    @QCManager().handle_error()
    def _handle_response(self, response, request_id, query, current_date, all_tweets, records_fetched):
        self.qc_manager.log_debug(f"Handling API response for request ID: {request_id}, query: {query}, date: {current_date}", context="XTwitterRetriever")
        if 'data' in response and response['data'] is not None:
            tweets = response['data']
            all_tweets.extend(tweets)
            num_tweets = len(tweets)
            self._save_tweets(tweets, request_id, query, current_date)
            self.qc_manager.log_debug(f"Scraped and saved {num_tweets} tweets for {query} on {current_date.strftime('%Y-%m-%d')}.", context="XTwitterRetriever")
            self.qc_manager.log_debug(f"Processed {num_tweets} tweets from the API response", context="XTwitterRetriever")
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

        self.qc_manager.log_debug(f"Extracted date range: start_date={start_date}, end_date={end_date}", context="XTwitterRetriever")
        return start_date, end_date, query