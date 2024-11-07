"""
Module for scraping tweets from the XTwitter API in the MASA project.

This module provides the XTwitterScraper class, which handles the scraping
of tweets from the XTwitter API, including pagination, error handling, and
data storage.
"""

import time
from datetime import datetime, timedelta
import re
from ...connections.xtwitter_connection import XTwitterConnection
from masa_ai.tools.qc.qc_manager import QCManager
from masa_ai.tools.qc.exceptions import ConfigurationException, DataProcessingException, APIException
from masa_ai.configs.config import global_settings
from masa_ai.tools.utils.tweet_stats import TweetStats
from masa_ai.tools.database.duckdb_handler import DuckDBHandler
from masa_ai.tools.database.abstract_database_handler import AbstractDatabaseHandler
from typing import Optional

class XTwitterScraper:
    """
    XTwitter data scraper for the MASA project.

    This class handles the scraping of tweets from the XTwitter API,
    including pagination, error handling, and data storage.

    Attributes:
        qc_manager (masa_ai.tools.qc.qc_manager.QCManager): The quality control manager for logging and error handling.
        state_manager (masa_ai.orchestration.state_manager.StateManager): The state manager to track scraping progress.
        request (dict): The request configuration for tweet scraping.
        twitter_connection (masa_ai.connections.xtwitter_connection.XTwitterConnection): The connection to the XTwitter API.
        db_handler (masa_ai.tools.database.duckdb_handler.DuckDBHandler): The database handler for storing tweets.
        tweet_stats (masa_ai.tools.stats.tweet_stats.TweetStats): The TweetStats instance for tracking statistics.
    """

    def __init__(self, state_manager, request, db_handler: Optional[AbstractDatabaseHandler] = None, tweet_stats: TweetStats = None):
        """
        Initialize the XTwitterScraper.

        Args:
            state_manager: The state manager to track scraping progress.
            request: The request configuration for tweet scraping.
            db_handler (AbstractDatabaseHandler, optional): Database handler for storing tweets.
            tweet_stats (TweetStats, optional): The TweetStats instance for tracking statistics.
        """
        self.qc_manager = QCManager()
        self.state_manager = state_manager
        self.request = request
        self.twitter_connection = XTwitterConnection()
        self.db_handler = db_handler
        self.tweet_stats = None
        
        if not self.db_handler:
            self.qc_manager.log_warning("No database handler provided. Tweets will not be stored.", context="XTwitterScraper")

    @QCManager().handle_error()
    def scrape_tweets(self, request_id, query, count):
        """
        Scrape tweets based on the given request.

        Args:
            request_id (str): The ID of the request.
            query (str): The search query for tweets.
            count (int): The number of tweets to scrape per API call.

        Returns:
            tuple: A tuple containing the scraped tweets, API call count, and number of records fetched.

        Raises:
            ConfigurationException: If required parameters are missing in the request.
            APIException: If there's an error in making the API request.
            RateLimitException: If the API rate limit is exceeded.
        """
        self.qc_manager.log_debug(f"Starting scrape_tweets for request: {request_id}", context="XTwitterScraper")
        
        self.tweet_stats = TweetStats(request_id, self.db_handler, self.qc_manager)
        
        request = self.state_manager.get_request_state(request_id)
        params = request.get('params', {})
        api_endpoint = self.request.get('endpoint')
        

        self.qc_manager.log_debug(f"Query: {query}, Count: {count} for {api_endpoint}", context="XTwitterScraper")

        if not all([query, count, api_endpoint]):
            raise ConfigurationException("Missing required parameters in request")

        # Extract time-related parameters
        start_date, end_date, cleaned_query = self._extract_date_range(query)
        
        self.qc_manager.log_debug(f"Extracted date range: {start_date} to {end_date}", context="XTwitterScraper")
        
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

        self.qc_manager.log_info(f"Starting tweet scraping for query: {query} over {total_days} days", context="XTwitterScraper")

        all_tweets = []
        api_calls_count = 0
        records_fetched = 0
        days_processed = 0

        while current_date >= start_date:
            
            iteration_end_date = current_date
            iteration_start_date = current_date

            query_until_date = (iteration_end_date + timedelta(days=1)).strftime('%Y-%m-%d')
            date_range_query = f"{cleaned_query} since:{iteration_start_date.strftime('%Y-%m-%d')} until:{query_until_date}"
            
            self.qc_manager.log_debug(f"Processing date: {iteration_start_date}", context="XTwitterScraper")
            self.qc_manager.log_debug(f"Calling twitter_connection.get_tweets with query: {date_range_query}, count: {count}, start_time: {current_date}, end_time: {current_date + timedelta(days=1)}", context="XTwitterScraper")
            
            try:
                time_start = time.time()
                response = self.twitter_connection.get_tweets(api_endpoint, date_range_query, count)
                time_end = time.time()
                elapsed_time = time_end - time_start

                self.tweet_stats.update_response_time(elapsed_time)
                self.qc_manager.log_debug(f"API response time: {elapsed_time:.2f} seconds", context="XTwitterScraper")
                
                self.qc_manager.log_debug(f"Received response from API", context="XTwitterScraper")
            
            except Exception as e:
                self.qc_manager.log_error(f"API call failed: {str(e)}", context="XTwitterScraper")
                raise
            
            api_calls_count += 1
            new_records = self._handle_response(response, request_id, query, iteration_end_date, all_tweets, records_fetched)
            records_fetched += new_records
            self.qc_manager.log_debug(f"Received {new_records} tweets from API, total records fetched: {records_fetched}", context="XTwitterScraper")

            days_processed += 1
            progress_percentage = min(100, int((days_processed / total_days) * 100))
            self.qc_manager.log_info(f"Tweet scraping progress: {progress_percentage}% ({records_fetched} tweets fetched)", context="XTwitterScraper")

            current_date -= timedelta(days=1)
            self.state_manager.update_request_state(request_id, 'in_progress', {'last_processed_time': current_date.isoformat()})

            # Pause for the configured success wait time before the next iteration
            success_wait_time = global_settings.get('twitter.SUCCESS_WAIT_TIME', 5)

            self.qc_manager.log_debug(f"Pausing for {success_wait_time} seconds before the next iteration", context="XTwitterScraper")

            time.sleep(success_wait_time)

            # Update and log scraping statistics
            self.qc_manager.log_info(self.tweet_stats.get_colored_stats(), context="TweetStats")

       

        self.qc_manager.log_info(f"Tweet scraping completed for query: {query} over {total_days} days. Total tweets: {records_fetched}, API calls: {api_calls_count}", context="XTwitterScraper")
        return all_tweets, api_calls_count, records_fetched

    @QCManager().handle_error()
    def _handle_response(self, response, request_id, query, current_date, all_tweets, records_fetched):
        """
        Handle the response from the XTwitter API.

        Args:
            response (dict): The response from the XTwitter API.
            request_id (str): The ID of the current request.
            query (str): The search query used for scraping tweets.
            current_date (datetime): The current date being processed.
            all_tweets (list): The list to store all scraped tweets.
            records_fetched (int): The total number of records fetched so far.

        Returns:
            int: The number of new tweets processed from the API response.
        """
        self.qc_manager.log_debug(f"Handling API response for request ID: {request_id}, query: {query}, date: {current_date}", context="XTwitterScraper")
        
        if response is None:
            self.qc_manager.log_error("Received empty response from API.", context="XTwitterScraper._handle_response")
            raise APIException("Empty response from API.")
        
        if 'data' in response and response['data'] is not None:
            tweets = response['data']
            all_tweets.extend(tweets)
            num_tweets = len(tweets)
            self._save_tweets(tweets, request_id, query, current_date)

            self.qc_manager.log_debug(f"Scraped and saved {num_tweets} tweets for {query} on {current_date.strftime('%Y-%m-%d')}.", context="XTwitterScraper")
            self.qc_manager.log_debug(f"Processed {num_tweets} tweets from the API response", context="XTwitterScraper")

            # Update stats with worker ID from response or use a default
            worker_id = response.get('worker_id', f'worker_{current_thread().name}')
            self.tweet_stats.update(num_tweets, response.get('response_time', 0), worker_id)

            return num_tweets
        else:
            self.qc_manager.log_debug(f"No tweets fetched for {query} on {current_date.strftime('%Y-%m-%d')}. Likely no results.", context="XTwitterScraper")
            return 0

    def _save_tweets(self, tweets, request_id, query, current_date):
        """
        Save the scraped tweets to the database.

        Args:
            tweets (list): The list of tweets to save.
            request_id (str): The ID of the current request.
            query (str): The search query used for scraping tweets.
            current_date (datetime): The current date being processed.

        Raises:
            DataProcessingException: If there's an error saving the tweets.
        """
        try:
            if self.db_handler:
                self.db_handler.store_tweets(tweets, request_id)
            else:
                self.qc_manager.log_warning("No database handler available. Tweets not stored.", context="XTwitterScraper")
        except Exception as e:
            raise DataProcessingException(f"Failed to save tweets: {str(e)}")
        
        self.state_manager.update_request_state(request_id, 'in_progress', {
            'last_processed_time': current_date.isoformat(),
            'tweets_count': len(tweets)
        })

    def _extract_date_range(self, query):
        """
        Extract the date range from the search query.

        This method parses the search query to extract the 'since' and 'until' dates,
        and returns the cleaned query without the date range parameters.

        Args:
            query (str): The search query to extract the date range from.

        Returns:
            tuple: A tuple containing the start date, end date, and cleaned query.
        """
        self.qc_manager.log_debug(f"Query: {query}", context="XTwitterScraper")
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

        self.qc_manager.log_debug(f"Extracted date range: start_date={start_date}, end_date={end_date}", context="XTwitterScraper")
        return start_date, end_date, query