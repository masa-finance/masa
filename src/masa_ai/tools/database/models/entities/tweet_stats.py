from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy import String, Integer, Float, JSON, TIMESTAMP, func, Sequence
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

@dataclass
class TweetStats(Base):
    """Tweet statistics for scraping requests.
    
    Tracks statistics about tweet scraping jobs including total tweets fetched,
    API response times, and worker information.
    
    Args:
        request_id (str): ID of the associated scraping request.
        total_tweets (int): Total number of tweets fetched.
        api_call_count (int): Number of API calls made.
        total_response_time (float): Total time taken for API responses.
        unique_workers (List[str]): List of worker IDs that processed the request.
        created_at (datetime): Timestamp when stats were created.
        updated_at (datetime): Timestamp when stats were last updated.
    
    Attributes:
        to_dict (Callable[[], Dict[str, Any]]): Convert stats to dictionary with calculated metrics.
    """
    __tablename__ = 'tweet_stats'

    id: Mapped[int] = mapped_column(
        Integer,
        Sequence('tweet_stats_id_seq'),
        primary_key=True,
        init=False
    )
    request_id: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    
    total_tweets: Mapped[int] = mapped_column(
        Integer, 
        default=0
    )
    api_call_count: Mapped[int] = mapped_column(
        Integer, 
        default=0
    )
    total_response_time: Mapped[float] = mapped_column(
        Float, 
        default=0.0
    )
    unique_workers: Mapped[List[str]] = mapped_column(
        JSON, 
        default_factory=list
    )
    
    # Timestamp fields
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        default=func.now(),
        init=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        default=func.now(),
        onupdate=func.now(),
        init=False
    )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert tweet stats to dictionary.
    
        Returns:
            Dict[str, Any]: Dictionary representation of tweet stats including
                calculated metrics like average response time and tweets per minute.
        """
        return {
            'request_id': self.request_id,
            'total_tweets': self.total_tweets,
            'api_call_count': self.api_call_count,
            'total_response_time': self.total_response_time,
            'unique_workers': self.unique_workers,
            'avg_response_time': (
                self.total_response_time / self.api_call_count 
                if self.api_call_count else 0
            ),
            'tweets_per_minute': (
                self.total_tweets / self.total_response_time * 60 
                if self.total_response_time else 0
            ),
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
