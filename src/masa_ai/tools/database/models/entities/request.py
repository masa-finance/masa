from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy import JSON, String, Integer, TIMESTAMP, Sequence
from sqlalchemy.orm import Mapped, mapped_column, relationship

from masa_ai.tools.database.models.base import Base

class Request(Base):
    """Request entity for storing API request information.
    
    Args:
        request_id: Unique identifier for the request
        scraper: Name of the scraper being used
        endpoint: API endpoint for the request
        params: Additional parameters for the request
        priority: Priority level of the request
        status: Current status of the request
        result: Result data from the request
        error: Error message if request failed
        created_at: Timestamp when request was created
        updated_at: Timestamp when request was last updated
    """
    __tablename__ = 'requests'

    id: Mapped[int] = mapped_column(
        Integer,
        Sequence('request_id_seq'),
        primary_key=True,
        nullable=False,
        init=False
    )
    request_id: Mapped[str] = mapped_column(String, nullable=False)
    scraper: Mapped[str] = mapped_column(String, nullable=False)
    endpoint: Mapped[str] = mapped_column(String, nullable=False)
    params: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String, nullable=False, default='pending')
    result: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default_factory=dict
    )
    error: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default_factory=datetime.utcnow,
        init=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default_factory=datetime.utcnow,
        onupdate=datetime.utcnow,
        init=False
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert request object to dictionary.
        
        Returns:
            Dict containing all request attributes
        """
        return {
            'id': self.id,
            'request_id': self.request_id,
            'scraper': self.scraper,
            'endpoint': self.endpoint,
            'params': self.params,
            'priority': self.priority,
            'status': self.status,
            'result': self.result,
            'error': self.error,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    tweets: Mapped[List["Tweet"]] = relationship(
        "Tweet",
        back_populates="request",
        init=False
    )