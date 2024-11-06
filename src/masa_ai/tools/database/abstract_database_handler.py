from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class AbstractDatabaseHandler(ABC):
    """Abstract base class defining the interface for database operations.
    
    This class provides the contract that all concrete database handlers must implement.
    It defines methods for basic CRUD operations and specialized operations for managing
    requests, tweets, stats and logs.
    """

    @abstractmethod
    def connect(self) -> None:
        """Establish a synchronous connection to the database."""
        pass

    @abstractmethod 
    async def connect_async(self) -> None:
        """Establish an asynchronous connection to the database."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close the synchronous connection to the database."""
        pass

    @abstractmethod
    async def disconnect_async(self) -> None:
        """Close the asynchronous connection to the database."""
        pass

    @abstractmethod
    def add_request(self, request: Dict[str, Any]) -> None:
        """Add a new request to the database synchronously.

        Args:
            request (Dict[str, Any]): The request data to add.
        """
        pass

    @abstractmethod
    async def add_request_async(self, request: Dict[str, Any]) -> None:
        """Add a new request to the database asynchronously.

        Args:
            request (Dict[str, Any]): The request data to add.
        """
        pass

    @abstractmethod
    def update_request_status(self, request_id: str, status: str, progress: Dict[str, Any]) -> None:
        """Update the status and progress of an existing request synchronously.

        Args:
            request_id (str): The ID of the request to update.
            status (str): The new status.
            progress (Dict[str, Any]): Progress information.
        """
        pass

    @abstractmethod
    async def update_request_status_async(self, request_id: str, status: str, progress: Dict[str, Any]) -> None:
        """Update the status and progress of an existing request asynchronously.

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
            Dict[str, Any]: The request data.
        """
        pass

    @abstractmethod
    async def get_request_by_id_async(self, request_id: str) -> Dict[str, Any]:
        """Retrieve a request by its ID asynchronously.

        Args:
            request_id (str): The ID of the request.

        Returns:
            Dict[str, Any]: The request data.
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
        """Add a request to the queue synchronously.

        Args:
            request_id (str): The ID of the request to enqueue.
            priority (int, optional): Priority level. Defaults to 1.
        """
        pass

    @abstractmethod
    async def enqueue_request_async(self, request_id: str, priority: int = 1) -> None:
        """Add a request to the queue asynchronously.

        Args:
            request_id (str): The ID of the request to enqueue.
            priority (int, optional): Priority level. Defaults to 1.
        """
        pass

    @abstractmethod
    def store_tweets(self, tweets: List[Dict[str, Any]], request_id: str) -> None:
        """Store tweets in the database synchronously.

        Args:
            tweets (List[Dict[str, Any]]): List of tweet data to store.
            request_id (str): The ID of the associated request.
        """
        pass

    @abstractmethod
    async def store_tweets_async(self, tweets: List[Dict[str, Any]], request_id: str) -> None:
        """Store tweets in the database asynchronously.

        Args:
            tweets (List[Dict[str, Any]]): List of tweet data to store.
            request_id (str): The ID of the associated request.
        """
        pass

    @abstractmethod
    def update_stats(self, request_id: str, new_tweets: int, response_time: float, worker_id: str) -> None:
        """Update tweet statistics for a request synchronously.

        Args:
            request_id (str): The ID of the request.
            new_tweets (int): Number of new tweets added.
            response_time (float): API response time.
            worker_id (str): ID of the worker processing the request.
        """
        pass

    @abstractmethod
    async def update_stats_async(self, request_id: str, new_tweets: int, response_time: float, worker_id: str) -> None:
        """Update tweet statistics for a request asynchronously.

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
            Dict[str, Any]: Statistics for the request.
        """
        pass

    @abstractmethod
    async def get_stats_async(self, request_id: str) -> Dict[str, Any]:
        """Get tweet statistics for a request asynchronously.

        Args:
            request_id (str): The ID of the request.

        Returns:
            Dict[str, Any]: Statistics for the request.
        """
        pass

    @abstractmethod
    def log_message(self, level: str, message: str, context: str = "", error_info: Any = None) -> None:
        """Log a message to the database synchronously.

        Args:
            level (str): Log level.
            message (str): Log message.
            context (str, optional): Context of the log. Defaults to "".
            error_info (Any, optional): Additional error information. Defaults to None.
        """
        pass

    @abstractmethod
    async def log_message_async(self, level: str, message: str, context: str = "", error_info: Any = None) -> None:
        """Log a message to the database asynchronously.

        Args:
            level (str): Log level.
            message (str): Log message.
            context (str, optional): Context of the log. Defaults to "".
            error_info (Any, optional): Additional error information. Defaults to None.
        """
        pass

    @abstractmethod
    def get_logs(self, limit: int = 100, level: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve logs from the database synchronously.

        Args:
            limit (int, optional): Maximum number of logs to return. Defaults to 100.
            level (Optional[str], optional): Filter by log level. Defaults to None.

        Returns:
            List[Dict[str, Any]]: List of log entries.
        """
        pass

    @abstractmethod
    async def get_logs_async(self, limit: int = 100, level: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve logs from the database asynchronously.

        Args:
            limit (int, optional): Maximum number of logs to return. Defaults to 100.
            level (Optional[str], optional): Filter by log level. Defaults to None.

        Returns:
            List[Dict[str, Any]]: List of log entries.
        """
        pass


