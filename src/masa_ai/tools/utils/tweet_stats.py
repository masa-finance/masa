"""
Module for tracking statistics related to tweet scraping jobs.

This module provides the TweetStats class, which handles the collection
and logging of statistics such as total tweets fetched, average response
time, tweets per minute, and unique workers involved in the scraping process.
"""

import time
from statistics import mean
from masa_ai.tools.qc.qc_manager import QCManager

class TweetStats:
    """
    Class to track and log statistics for tweet scraping jobs.

    Attributes:
        total_tweets (int): Total number of tweets fetched.
        api_call_count (int): Total number of API calls made.
        total_response_time (float): Total time taken for all API calls.
        unique_workers (set): Set of unique worker IDs that fetched tweets.
        qc_manager (masa_ai.tools.qc.qc_manager.QCManager): Quality control manager for logging.
    """

    def __init__(self, qc_manager: QCManager):
        """
        Initialize the TweetStats instance.

        Args:
            qc_manager (masa_ai.tools.qc.qc_manager.QCManager): The QCManager instance for logging.
        """
        self.total_tweets = 0
        self.api_call_count = 0
        self.total_response_time = 0.0
        self.unique_workers = set()
        self.qc_manager = qc_manager

    def update(self, new_tweets: int, response_time: float, worker_id: str):
        """
        Update the statistics with new data.

        Args:
            new_tweets (int): Number of new tweets fetched.
            response_time (float): Time taken for the API response.
            worker_id (str): ID of the worker that fetched the tweets.
        """
        self.total_tweets += new_tweets
        self.update_response_time(response_time)
        self.unique_workers.add(worker_id)

    def update_response_time(self, elapsed_time: float):
        """
        Update the total and average response time with the latest API call.

        Args:
            elapsed_time (float): The elapsed time for the API response.
        """
        self.total_response_time += elapsed_time
        self.api_call_count += 1

    def get_stats(self) -> tuple:
        """
        Calculate and return the current statistics.

        Returns:
            tuple: Total tweets, average response time, tweets per minute, unique workers.
        """
        avg_response_time = (self.total_response_time / self.api_call_count) if self.api_call_count else 0
        tweets_per_minute = (self.total_tweets / self.total_response_time * 60) if self.total_response_time else 0
        unique_workers = len(self.unique_workers)
        return self.total_tweets, avg_response_time, tweets_per_minute, unique_workers

    def get_colored_stats(self) -> str:
        """
        Get the statistics as a colored string for logging.

        Returns:
            str: Colored statistics string.
        """
        total_tweets, avg_response_time, tweets_per_minute, unique_workers = self.get_stats()
        # ANSI escape code for yellow text
        colored_stats = (
            f"\033[93mTotal tweets: {total_tweets}, "
            f"Avg response time: {avg_response_time:.2f}s, "
            f"Tweets/min: {tweets_per_minute:.2f}, "
            f"Unique workers: {unique_workers}\033[0m"
        )
        return colored_stats 