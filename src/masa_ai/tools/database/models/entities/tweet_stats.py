
from dataclasses import dataclass, field
from typing import List, Dict, Any
from sqlalchemy import Column, String, Integer, Float, JSON
from masa_ai.tools.database.models.base import Base

@dataclass
class TweetStats(Base):
    """Tweet statistics for scraping requests.
    
    Tracks statistics about tweet scraping jobs including total tweets fetched,
    API response times, and worker information.

    Args:
        request_id (str): ID of the associated scraping request
        total_tweets (int): Total number of tweets fetched
        api_call_count (int): Number of API calls made
        total_response_time (float): Total time taken for API responses
        unique_workers (List[str]): List of worker IDs that processed the request

    Attributes:
        request_id (str): ID of the associated scraping request
        total_tweets (int): Total number of tweets fetched
        api_call_count (int): Number of API calls made 
        total_response_time (float): Total time taken for API responses
        unique_workers (List[str]): List of worker IDs that processed the request
    """
    __tablename__ = 'tweet_stats'

    # SQLAlchemy columns
    request_id = Column(String, primary_key=True)
    total_tweets = Column(Integer, nullable=False, default=0)
    api_call_count = Column(Integer, nullable=False, default=0)
    total_response_time = Column(Float, nullable=False, default=0.0)
    unique_workers = Column(JSON, nullable=False, default=list)

    # Dataclass fields
    request_id: str = field(init=False)
    total_tweets: int = field(default=0)
    api_call_count: int = field(default=0) 
    total_response_time: float = field(default=0.0)
    unique_workers: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert tweet stats to dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of tweet stats
        """
        return {
            'request_id': self.request_id,
            'total_tweets': self.total_tweets,
            'api_call_count': self.api_call_count,
            'total_response_time': self.total_response_time,
            'unique_workers': self.unique_workers,
            'avg_response_time': (self.total_response_time / self.api_call_count 
                                if self.api_call_count else 0),
            'tweets_per_minute': (self.total_tweets / self.total_response_time * 60 
                                if self.total_response_time else 0)
        }
