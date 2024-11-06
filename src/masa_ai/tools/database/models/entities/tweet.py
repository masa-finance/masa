from dataclasses import dataclass, field
from typing import Dict, Any
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship

from ..base import Base

@dataclass
class Tweet(Base):
    """Represents a tweet in the MASA project.
    
    Args:
        tweet_id (str): Unique identifier for the tweet.
        request_id (str): Identifier of the request that fetched this tweet.
        created_at (datetime): Timestamp when the tweet was created.
        text (str): Content of the tweet.
        user_id (str): Identifier of the user who posted the tweet.
        user_name (str): Name of the user who posted the tweet.
        additional_fields (Dict[str, Any]): Any additional fields from the tweet data.
    """
    __tablename__: str = "tweets"

    tweet_id: str = field(init=False, default='')
    request_id: str = field(default='')
    created_at: datetime = field(default_factory=lambda: datetime.now(datetime.UTC))
    text: str = field(default='')
    user_id: str = field(default='')
    user_name: str = field(default='')
    additional_fields: Dict[str, Any] = field(default_factory=dict)

    # SQLAlchemy Columns
    tweet_id = Column(String, primary_key=True)
    request_id = Column(String, ForeignKey('requests.request_id'), nullable=False)
    created_at = Column(DateTime, nullable=False)
    text = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    user_name = Column(String, nullable=False)
    additional_fields = Column(JSON, nullable=True)

    # Relationships
    request = relationship("Request", back_populates="tweets")
