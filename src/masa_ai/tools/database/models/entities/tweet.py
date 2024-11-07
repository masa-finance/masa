from __future__ import annotations
from typing import Dict, Any, List, TYPE_CHECKING
from datetime import UTC, datetime
from sqlalchemy import JSON, String, Integer, ForeignKey, TIMESTAMP, Sequence
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .request import Request

class Tweet(Base):
    """Tweet entity for storing tweet data.
    
    Args:
        tweet_id: Unique Twitter ID for the tweet
        request_id: ID of the associated request
        text: Tweet content
        user_id: Twitter user ID
        user_name: Twitter user's display name
        username: Twitter username
        conversation_id: ID of the conversation thread
        created_at: Tweet creation timestamp
        likes: Number of likes
        retweets: Number of retweets
        replies: Number of replies
        views: Number of views
        hashtags: List of hashtags in the tweet
        mentions: List of user mentions
        urls: List of URLs in the tweet
        photos: List of photo information
        additional_fields: Additional metadata
    """
    __tablename__ = "tweets"

    # Required fields first (no defaults)
    tweet_id: Mapped[str] = mapped_column(String, nullable=False)
    request_id: Mapped[int] = mapped_column(ForeignKey("requests.id"), nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    user_name: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=False)
    conversation_id: Mapped[str] = mapped_column(String, nullable=False)
    
    # Auto-generated fields
    id: Mapped[int] = mapped_column(
        Integer,
        Sequence('tweet_id_seq'),
        primary_key=True,
        init=False
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default_factory=lambda: datetime.now(UTC)
    )

    # Optional fields with defaults
    likes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    retweets: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    replies: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    views: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    hashtags: Mapped[List[str]] = mapped_column(
        JSON, nullable=False, default_factory=list
    )
    mentions: Mapped[List[Dict[str, str]]] = mapped_column(
        JSON, nullable=False, default_factory=list
    )
    urls: Mapped[List[str]] = mapped_column(
        JSON, nullable=False, default_factory=list
    )
    photos: Mapped[List[Dict[str, str]]] = mapped_column(
        JSON, nullable=False, default_factory=list
    )
    additional_fields: Mapped[Dict[str, Any]] = mapped_column(
        JSON, nullable=False, default_factory=dict
    )

    request: Mapped["Request"] = relationship(back_populates="tweets", init=False)