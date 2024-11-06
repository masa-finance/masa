import json
import asyncio
from typing import Any, Dict, List, Optional
from sqlalchemy import create_engine, select, update, delete, insert
from sqlalchemy.orm import sessionmaker, Session

from masa_ai.tools.database.abstract_database_handler import AbstractDatabaseHandler
from masa_ai.tools.database.models.base import Base
from masa_ai.tools.database.models.entities.request import Request
from masa_ai.tools.database.models.entities.tweet import Tweet
from masa_ai.tools.database.models.entities.tweet_stats import TweetStats


class DuckDBHandler(AbstractDatabaseHandler):
    """Concrete implementation of AbstractDatabaseHandler for DuckDB using SQLAlchemy.
    
    This class handles all database operations using DuckDB as the backend through SQLAlchemy ORM.
    It implements the full AbstractDatabaseHandler interface with both
    synchronous and asynchronous methods.
    """

    def __init__(self, database_path: str, qc_manager: 'QCManager'):
        """Initialize DuckDBHandler with database path and QC manager.

        Args:
            database_path (str): Path to the DuckDB database file
            qc_manager (QCManager): Quality control manager for logging
        """
        self.database_path = database_path
        self.engine = None
        self.Session = None
        self.qc_manager = qc_manager

    def connect(self) -> None:
        """Establish synchronous connection to DuckDB database."""
        self.engine = create_engine(f"duckdb:///{self.database_path}")
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    async def connect_async(self) -> None:
        """Establish asynchronous connection to DuckDB database."""
        await asyncio.to_thread(self.connect)

    def disconnect(self) -> None:
        """Close synchronous database connection."""
        if self.engine:
            self.engine.dispose()
            self.engine = None
            self.Session = None

    async def disconnect_async(self) -> None:
        """Close asynchronous database connection."""
        if self.engine:
            await asyncio.to_thread(self.disconnect)

    def add_request(self, request: Dict[str, Any]) -> None:
        """Add new request to database synchronously."""
        try:
            with self.Session() as session:
                new_request = Request(
                    request_id=request['request_id'],
                    status=request['status'],
                    params=request['params']
                )
                session.add(new_request)
                session.commit()
            self.qc_manager.log_info(f"Added request {request['request_id']}", context="DuckDBHandler")
        except Exception as e:
            self.qc_manager.log_error(f"Failed to add request: {e}", context="DuckDBHandler")
            raise

    async def add_request_async(self, request: Dict[str, Any]) -> None:
        """Add new request to database asynchronously."""
        await asyncio.to_thread(self.add_request, request)

    def update_request_status(self, request_id: str, status: str, progress: Dict[str, Any]) -> None:
        """Update request status synchronously."""
        try:
            with self.Session() as session:
                stmt = update(Request).where(Request.request_id == request_id).values(status=status)
                session.execute(stmt)
                session.commit()
            self.qc_manager.log_info(f"Updated status of request {request_id} to {status}", context="DuckDBHandler")
        except Exception as e:
            self.qc_manager.log_error(f"Failed to update request status: {e}", context="DuckDBHandler")
            raise

    async def update_request_status_async(self, request_id: str, status: str, progress: Dict[str, Any]) -> None:
        """Update request status asynchronously."""
        await asyncio.to_thread(self.update_request_status, request_id, status, progress)

    def get_request_by_id(self, request_id: str) -> Dict[str, Any]:
        """Get request by ID synchronously."""
        try:
            with self.Session() as session:
                request = session.query(Request).filter(Request.request_id == request_id).first()
                if request:
                    return request.to_dict()
                return {}
        except Exception as e:
            self.qc_manager.log_error(f"Failed to get request: {e}", context="DuckDBHandler")
            raise

    async def get_request_by_id_async(self, request_id: str) -> Dict[str, Any]:
        """Get request by ID asynchronously."""
        return await asyncio.to_thread(self.get_request_by_id, request_id)

    def get_all_requests(self) -> List[Dict[str, Any]]:
        """Get all requests synchronously."""
        try:
            with self.Session() as session:
                requests = session.query(Request).all()
                return [request.to_dict() for request in requests]
        except Exception as e:
            self.qc_manager.log_error(f"Failed to get all requests: {e}", context="DuckDBHandler")
            raise

    async def get_all_requests_async(self) -> List[Dict[str, Any]]:
        """Get all requests asynchronously."""
        return await asyncio.to_thread(self.get_all_requests)

    def remove_request(self, request_id: str) -> None:
        """Remove request synchronously."""
        try:
            with self.Session() as session:
                stmt = delete(Request).where(Request.request_id == request_id)
                session.execute(stmt)
                session.commit()
            self.qc_manager.log_info(f"Removed request {request_id}", context="DuckDBHandler")
        except Exception as e:
            self.qc_manager.log_error(f"Failed to remove request: {e}", context="DuckDBHandler")
            raise

    async def remove_request_async(self, request_id: str) -> None:
        """Remove request asynchronously."""
        await asyncio.to_thread(self.remove_request, request_id)

    def enqueue_request(self, request_id: str, priority: int = 1) -> None:
        """Enqueue request synchronously."""
        try:
            with self.Session() as session:
                stmt = update(Request).where(Request.request_id == request_id).values(status='queued')
                session.execute(stmt)
                session.commit()
            self.qc_manager.log_info(f"Enqueued request {request_id}", context="DuckDBHandler")
        except Exception as e:
            self.qc_manager.log_error(f"Failed to enqueue request: {e}", context="DuckDBHandler")
            raise

    async def enqueue_request_async(self, request_id: str, priority: int = 1) -> None:
        """Enqueue request asynchronously."""
        await asyncio.to_thread(self.enqueue_request, request_id, priority)

    def store_tweets(self, tweets: List[Dict[str, Any]], request_id: str) -> None:
        """Store tweets synchronously."""
        try:
            with self.Session() as session:
                for tweet_data in tweets:
                    tweet = Tweet(
                        tweet_id=tweet_data['id'],
                        request_id=request_id,
                        created_at=tweet_data['created_at'],
                        text=tweet_data['text'],
                        user_id=tweet_data['user']['id'],
                        user_name=tweet_data['user']['name']
                    )
                    session.add(tweet)
                session.commit()
            self.qc_manager.log_info(f"Stored {len(tweets)} tweets for request {request_id}", context="DuckDBHandler")
        except Exception as e:
            self.qc_manager.log_error(f"Failed to store tweets: {e}", context="DuckDBHandler")
            raise

    async def store_tweets_async(self, tweets: List[Dict[str, Any]], request_id: str) -> None:
        """Store tweets asynchronously."""
        await asyncio.to_thread(self.store_tweets, tweets, request_id)

    def update_stats(self, request_id: str, new_tweets: int, response_time: float, worker_id: str) -> None:
        """Update tweet statistics synchronously."""
        try:
            with self.Session() as session:
                stats = session.query(TweetStats).filter(TweetStats.request_id == request_id).first()
                if stats:
                    unique_workers = set(stats.unique_workers)
                    unique_workers.add(worker_id)
                    stats.total_tweets += new_tweets
                    stats.api_call_count += 1
                    stats.total_response_time += response_time
                    stats.unique_workers = list(unique_workers)
                else:
                    stats = TweetStats(
                        request_id=request_id,
                        total_tweets=new_tweets,
                        api_call_count=1,
                        total_response_time=response_time,
                        unique_workers=[worker_id]
                    )
                    session.add(stats)
                session.commit()
            self.qc_manager.log_info(f"Updated stats for request {request_id}", context="DuckDBHandler")
        except Exception as e:
            self.qc_manager.log_error(f"Failed to update stats: {e}", context="DuckDBHandler")
            raise

    async def update_stats_async(self, request_id: str, new_tweets: int, response_time: float, worker_id: str) -> None:
        """Update tweet statistics asynchronously."""
        await asyncio.to_thread(self.update_stats, request_id, new_tweets, response_time, worker_id)

    def get_stats(self, request_id: str) -> Dict[str, Any]:
        """Get tweet statistics synchronously."""
        try:
            with self.Session() as session:
                stats = session.query(TweetStats).filter(TweetStats.request_id == request_id).first()
                if stats:
                    return stats.to_dict()
                return {}
        except Exception as e:
            self.qc_manager.log_error(f"Failed to get stats: {e}", context="DuckDBHandler")
            raise

    async def get_stats_async(self, request_id: str) -> Dict[str, Any]:
        """Get tweet statistics asynchronously."""
        return await asyncio.to_thread(self.get_stats, request_id)
    
    # TODO: Logging functionality if we want to keep it in a table ever.

    # def log_message(self, level: str, message: str, context: str = "", error_info: Any = None) -> None:
    #     """Log message synchronously."""
    #     try:
    #         with self.Session() as session:
    #             log = Log(
    #                 level=level,
    #                 message=message,
    #                 context=context,
    #                 error_info=error_info
    #             )
    #             session.add(log)
    #             session.commit()
    #     except Exception as e:
    #         self.qc_manager.log_error(f"Failed to log message: {e}", context="DuckDBHandler")
    #         raise

    # async def log_message_async(self, level: str, message: str, context: str = "", error_info: Any = None) -> None:
    #     """Log message asynchronously."""
    #     await asyncio.to_thread(self.log_message, level, message, context, error_info)

    # def get_logs(self, limit: int = 100, level: Optional[str] = None) -> List[Dict[str, Any]]:
    #     """Get logs synchronously."""
    #     try:
    #         with self.Session() as session:
    #             query = session.query(Log)
    #             if level:
    #                 query = query.filter(Log.level == level)
    #             logs = query.order_by(Log.timestamp.desc()).limit(limit).all()
    #             return [log.to_dict() for log in logs]
    #     except Exception as e:
    #         self.qc_manager.log_error(f"Failed to get logs: {e}", context="DuckDBHandler")
    #         raise

    # async def get_logs_async(self, limit: int = 100, level: Optional[str] = None) -> List[Dict[str, Any]]:
    #     """Get logs asynchronously."""
    #     return await asyncio.to_thread(self.get_logs, limit, level)
