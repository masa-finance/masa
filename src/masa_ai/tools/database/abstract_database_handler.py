from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class AbstractDatabaseHandler(ABC):
    """Abstract base class defining the interface for database operations.
    
    This class provides the contract that all concrete database handlers must implement.
    It defines methods for basic CRUD operations and specialized operations for managing
    requests, tweets, and stats using SQLAlchemy ORM patterns.

    Attributes:
        database_path (str): Path to the database file
        engine: SQLAlchemy engine instance
        Session: SQLAlchemy session factory
        qc_manager (QCManager): Quality control manager for logging
    """

    @abstractmethod
    def __init__(self, database_path: str, qc_manager: 'QCManager'):
        """Initialize database handler with path and QC manager.

        Args:
            database_path (str): Path to the database file
            qc_manager (QCManager): Quality control manager for logging
        """
        pass

    @abstractmethod
    def connect(self) -> None:
        """Establish a synchronous connection to the database and initialize SQLAlchemy."""
        pass

    @abstractmethod 
    async def connect_async(self) -> None:
        """Establish an asynchronous connection to the database."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close the synchronous database connection and dispose SQLAlchemy engine."""
        pass

    @abstractmethod
    async def disconnect_async(self) -> None:
        """Close the asynchronous database connection."""
        pass

    @abstractmethod
    def add_request(self, request: Dict[str, Any]) -> None:
        """Add a new request to the database synchronously.

        Args:
            request (Dict[str, Any]): The request data containing request_id, status, and params.
        """
        pass

    @abstractmethod
    async def add_request_async(self, request: Dict[str, Any]) -> None:
        """Add a new request to the database asynchronously.

        Args:
            request (Dict[str, Any]): The request data containing request_id, status, and params.
        """
        pass

    @abstractmethod
    def update_request_status(self, request_id: str, status: str, progress: Dict[str, Any]) -> None:
        """Update the status of an existing request synchronously.

        Args:
            request_id (str): The ID of the request to update.
            status (str): The new status.
            progress (Dict[str, Any]): Progress information.
        """
        pass

    @abstractmethod
    async def update_request_status_async(self, request_id: str, status: str, progress: Dict[str, Any]) -> None:
        """Update the status of an existing request asynchronously.

        Args:
            request_id (str): The ID of the request to update.
            status (str): The new status.
            progress (Dict[str, Any]): Progress information.
        """
        pass

    @abstractmethod
    def get_request_by_id(self, request_id: str) -> Dict[str, Any]:
        """Retrieve a request by its ID synchronously.

        Args:
            request_id (str): The ID of the request.

        Returns:
            Dict[str, Any]: The request data or empty dict if not found.
        """
        pass

    @abstractmethod
    async def get_request_by_id_async(self, request_id: str) -> Dict[str, Any]:
        """Retrieve a request by its ID asynchronously.

        Args:
            request_id (str): The ID of the request.

        Returns:
            Dict[str, Any]: The request data or empty dict if not found.
        """
        pass

    @abstractmethod
    def get_all_requests(self) -> List[Dict[str, Any]]:
        """Retrieve all requests from the database synchronously.

        Returns:
            List[Dict[str, Any]]: List of all requests.
        """
        pass

    @abstractmethod
    async def get_all_requests_async(self) -> List[Dict[str, Any]]:
        """Retrieve all requests from the database asynchronously.

        Returns:
            List[Dict[str, Any]]: List of all requests.
        """
        pass

    @abstractmethod
    def remove_request(self, request_id: str) -> None:
        """Remove a request from the database synchronously.

        Args:
            request_id (str): The ID of the request to remove.
        """
        pass

    @abstractmethod
    async def remove_request_async(self, request_id: str) -> None:
        """Remove a request from the database asynchronously.

        Args:
            request_id (str): The ID of the request to remove.
        """
        pass

    @abstractmethod
    def enqueue_request(self, request_id: str, priority: int = 1) -> None:
        """Update request status to 'queued' synchronously.

        Args:
            request_id (str): The ID of the request to enqueue.
            priority (int, optional): Priority level. Defaults to 1.
        """
        pass

    @abstractmethod
    async def enqueue_request_async(self, request_id: str, priority: int = 1) -> None:
        """Update request status to 'queued' asynchronously.

        Args:
            request_id (str): The ID of the request to enqueue.
            priority (int, optional): Priority level. Defaults to 1.
        """
        pass

    @abstractmethod
    def store_tweets(self, tweets: List[Dict[str, Any]], request_id: str) -> None:
        """Store tweets in the database synchronously.

        Args:
            tweets (List[Dict[str, Any]]): List of tweet data containing id, created_at, text, user info.
            request_id (str): The ID of the associated request.
        """
        pass

    @abstractmethod
    async def store_tweets_async(self, tweets: List[Dict[str, Any]], request_id: str) -> None:
        """Store tweets in the database asynchronously.

        Args:
            tweets (List[Dict[str, Any]]): List of tweet data containing id, created_at, text, user info.
            request_id (str): The ID of the associated request.
        """
        pass

    @abstractmethod
    def update_stats(self, request_id: str, new_tweets: int, response_time: float, worker_id: str) -> None:
        """Update or create tweet statistics for a request synchronously.

        Args:
            request_id (str): The ID of the request.
            new_tweets (int): Number of new tweets added.
            response_time (float): API response time.
            worker_id (str): ID of the worker processing the request.
        """
        pass

    @abstractmethod
    async def update_stats_async(self, request_id: str, new_tweets: int, response_time: float, worker_id: str) -> None:
        """Update or create tweet statistics for a request asynchronously.

        Args:
            request_id (str): The ID of the request.
            new_tweets (int): Number of new tweets added.
            response_time (float): API response time.
            worker_id (str): ID of the worker processing the request.
        """
        pass

    @abstractmethod
    def get_stats(self, request_id: str) -> Dict[str, Any]:
        """Get tweet statistics for a request synchronously.

        Args:
            request_id (str): The ID of the request.

        Returns:
            Dict[str, Any]: Statistics for the request or empty dict if not found.
        """
        pass

    @abstractmethod
    async def get_stats_async(self, request_id: str) -> Dict[str, Any]:
        """Get tweet statistics for a request asynchronously.

        Args:
            request_id (str): The ID of the request.

        Returns:
            Dict[str, Any]: Statistics for the request or empty dict if not found.
        """
        pass
