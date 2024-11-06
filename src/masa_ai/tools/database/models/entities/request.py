from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, JSON
from sqlalchemy.orm import relationship

from ..base import Base

@dataclass
class Request(Base):
    """Represents a scraping request in the MASA project.
    
    Args:
        request_id (str): Unique identifier for the request.
        status (str): Current status of the request.
        created_at (datetime): Timestamp when the request was created.
        last_updated (datetime): Timestamp of the last update to the request.
        scraper (str): The scraper to be used (e.g., 'xtwitter').
        endpoint (str): API endpoint for the scraper.
        priority (int): Priority level of the request.
        params (Dict[str, Any]): Parameters for the scraping request.
        progress (Dict[str, Any]): Progress information of the request.
        result (Dict[str, Any]): Result data from the request.
        error (Optional[str]): Error message, if any.
        tweets (List['Tweet']): List of associated tweets.
    """
    __tablename__: str = "requests"

    request_id: str = field(init=False, default='')
    status: str = field(default='')
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    scraper: str = field(default='')
    endpoint: str = field(default='')
    priority: int = field(default=1)
    params: Dict[str, Any] = field(default_factory=dict)
    progress: Dict[str, Any] = field(default_factory=dict)
    result: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = field(default=None)
    tweets: List['Tweet'] = field(default_factory=list, compare=False)

    # SQLAlchemy Columns
    request_id = Column(String, primary_key=True)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    last_updated = Column(DateTime, nullable=False)
    scraper = Column(String, nullable=False)
    endpoint = Column(String, nullable=False)
    priority = Column(Integer, nullable=False)
    params = Column(JSON, nullable=False)
    progress = Column(JSON, nullable=False)
    result = Column(JSON, nullable=False)
    error = Column(String, nullable=True)

    # Relationships
    tweets = relationship("Tweet", back_populates="request")
