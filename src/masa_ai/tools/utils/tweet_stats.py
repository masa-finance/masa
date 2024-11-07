"""
Module for tracking statistics related to tweet scraping jobs.

This module provides the TweetStats class, which handles the collection
and logging of statistics such as total tweets fetched, average response
time, tweets per minute, and unique workers involved in the scraping process.
"""

from datetime import datetime, UTC
from typing import Optional, Dict, Any, Set
from masa_ai.tools.qc.qc_manager import QCManager
from masa_ai.tools.database.models.entities.tweet_stats import TweetStats as TweetStatsModel

class TweetStats:
    """
    Class to track and log statistics for tweet scraping jobs.
    
    This class maintains statistics in memory and syncs with the database
    through the DuckDB handler.

    Attributes:
        request_id (str): ID of the associated request
        total_tweets (int): Total number of tweets fetched
        api_call_count (int): Number of API calls made
        total_response_time (float): Total time spent on API calls
        unique_workers (Set[str]): Set of unique worker IDs
        db_handler (AbstractDatabaseHandler): Database handler for persistence
        qc_manager (QCManager): Quality control manager for logging
    """

    def __init__(self, request_id: str, db_handler: 'AbstractDatabaseHandler', qc_manager: QCManager):
        """
        Initialize the TweetStats instance.

        Args:
            request_id (str): ID of the associated request
            db_handler (AbstractDatabaseHandler): Database handler for persistence
            qc_manager (QCManager): Quality control manager for logging
        """
        self.request_id = request_id
        self.db_handler = db_handler
        self.qc_manager = qc_manager
        
        # Initialize stats from database or create new
        self._init_stats()

    def _init_stats(self) -> None:
        """Initialize statistics from database or create new stats record."""
        stats = self.db_handler.get_stats(self.request_id)
        
        if not stats:
            # Create new stats record in database
            self.db_handler.update_stats(
                request_id=self.request_id,
                new_tweets=0,
                response_time=0.0,
                worker_id=None,
                initialize=True
            )
            stats = self.db_handler.get_stats(self.request_id)
        
        self.total_tweets = stats['total_tweets']
        self.api_call_count = stats['api_call_count']
        self.total_response_time = stats['total_response_time']
        self.unique_workers = set(stats['unique_workers'])

    def update(self, new_tweets: int, response_time: float, worker_id: str) -> None:
        """
        Update statistics and persist to database.

        Args:
            new_tweets (int): Number of new tweets fetched
            response_time (float): Time taken for the API response
            worker_id (str): ID of the worker that fetched the tweets
        """
        try:
            self.total_tweets += new_tweets
            self.update_response_time(response_time)
            self.unique_workers.add(worker_id)
            
            # Persist updates to database
            self.db_handler.update_stats(
                request_id=self.request_id,
                new_tweets=new_tweets,
                response_time=response_time,
                worker_id=worker_id
            )
        except Exception as e:
            self.qc_manager.log_error(f"Error updating stats: {e}")
            raise

    def update_response_time(self, elapsed_time: float) -> None:
        """
        Update response time statistics.

        Args:
            elapsed_time (float): The elapsed time for the API response
        """
        self.total_response_time += elapsed_time
        self.api_call_count += 1

    def get_stats(self) -> Dict[str, Any]:
        """
        Get current statistics.

        Returns:
            Dict[str, Any]: Dictionary containing current statistics
        """
        return {
            'request_id': self.request_id,
            'total_tweets': self.total_tweets,
            'api_call_count': self.api_call_count,
            'total_response_time': self.total_response_time,
            'unique_workers': list(self.unique_workers),
            'avg_response_time': (
                self.total_response_time / self.api_call_count 
                if self.api_call_count else 0
            ),
            'tweets_per_minute': (
                self.total_tweets / self.total_response_time * 60 
                if self.total_response_time else 0
            )
        }

    def get_colored_stats(self) -> str:
        """
        Get statistics as a colored string for logging.

        Returns:
            str: Colored statistics string
        """
        stats = self.get_stats()
        return (
            f"\033[93m"
            f"Total tweets: {stats['total_tweets']}, "
            f"Avg response time: {stats['avg_response_time']:.2f}s, "
            f"Tweets/min: {stats['tweets_per_minute']:.2f}, "
            f"Unique workers: {len(stats['unique_workers'])}"
            f"\033[0m"
        )