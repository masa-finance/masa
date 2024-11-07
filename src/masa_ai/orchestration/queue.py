"""
Queue module for the MASA project.

This module provides a priority queue implementation for managing requests
in the MASA system, ensuring efficient processing based on request priorities.

The Queue class uses Python's built-in PriorityQueue to manage requests with priorities.
Lower priority values indicate higher priority.

Attributes:
    memory_queue (queue.PriorityQueue): The in-memory priority queue.
    qc_manager (tools.qc.qc_manager.QCManager): Quality control manager for logging.
    state_manager (orchestration.state_manager.StateManager): Manager for handling request states.
"""

from queue import PriorityQueue
from datetime import datetime
from typing import Optional, Tuple, Dict, Any, List

from masa_ai.tools.qc.qc_manager import QCManager
from masa_ai.tools.database.abstract_database_handler import AbstractDatabaseHandler

class Queue:
    """
    A priority queue implementation for managing requests using DuckDB backend.
    
    This class maintains an in-memory PriorityQueue that stays in sync with the database.
    Lower priority values indicate higher priority.
    """

    def __init__(self, db_handler: AbstractDatabaseHandler):
        """
        Initialize the Queue with database handler.

        Args:
            db_handler (AbstractDatabaseHandler): Database handler for persistent storage
        """
        self.memory_queue = PriorityQueue()
        self.db_handler = db_handler
        self.qc_manager = QCManager()
        
        # Initialize queue from database
        self._sync_with_database()

    def _sync_with_database(self) -> None:
        """
        Synchronize the in-memory queue with the database state.
        
        Loads all queued and in-progress requests from the database into the memory queue.
        """
        try:
            # Clear current memory queue
            self.memory_queue = PriorityQueue()
            
            # Get all requests from database
            requests = self.db_handler.get_all_requests()
            
            # Add active requests to memory queue
            for request in requests:
                if request['status'] in ['queued', 'in_progress']:
                    priority = request.get('priority', 100)
                    self.memory_queue.put((priority, request['request_id']))
            
            self.qc_manager.log_info(
                f"Synchronized queue with database. {self.memory_queue.qsize()} active requests loaded",
                context="Queue"
            )
        except Exception as e:
            self.qc_manager.log_error(f"Error syncing with database: {str(e)}", context="Queue")
            raise

    def add(self, request: Dict[str, Any]) -> None:
        """
        Add a request to the queue.

        Args:
            request (Dict[str, Any]): Request data to add
        """
        request_id = request['request_id']
        priority = request.get('priority', 100)
        
        try:
            # Add to database first
            self.db_handler.add_request(request)
            
            # Add to memory queue if not already present
            if not any(item[1] == request_id for item in self.memory_queue.queue):
                self.memory_queue.put((priority, request_id))
                self.qc_manager.log_debug(
                    f"Added request {request_id} with priority {priority}",
                    context="Queue"
                )
            else:
                self.qc_manager.log_debug(
                    f"Skipping duplicate request {request_id}",
                    context="Queue"
                )
        except Exception as e:
            self.qc_manager.log_error(f"Error adding request: {str(e)}", context="Queue")
            raise

    def get(self) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Get the next request from the queue.

        Returns:
            Tuple[Optional[str], Optional[Dict[str, Any]]]: Tuple of (request_id, request_data)
                or (None, None) if queue is empty
        """
        if self.memory_queue.empty():
            return None, None

        try:
            priority, request_id = self.memory_queue.get()
            request = self.db_handler.get_request_by_id(request_id)

            if not request:
                self.qc_manager.log_warning(
                    f"Request {request_id} not found in database",
                    context="Queue"
                )
                return None, None

            # Update status to in_progress in database
            self.db_handler.update_request_status(
                request_id,
                'in_progress',
                {'started_at': datetime.utcnow().isoformat()}
            )

            return request_id, request
        except Exception as e:
            self.qc_manager.log_error(f"Error retrieving request: {str(e)}", context="Queue")
            raise

    def complete(self, request_id: str) -> None:
        """
        Mark a request as completed.

        Args:
            request_id (str): ID of the request to complete
        """
        try:
            self.db_handler.update_request_status(
                request_id,
                'completed',
                {'completed_at': datetime.utcnow().isoformat()}
            )
            self.qc_manager.log_debug(f"Request {request_id} marked as completed", context="Queue")
        except Exception as e:
            self.qc_manager.log_error(f"Error completing request: {str(e)}", context="Queue")
            raise

    def fail(self, request_id: str, error: str) -> None:
        """
        Mark a request as failed.

        Args:
            request_id (str): ID of the request that failed
            error (str): Error message
        """
        try:
            self.db_handler.update_request_status(
                request_id,
                'failed',
                {
                    'error': str(error),
                    'failed_at': datetime.utcnow().isoformat()
                }
            )
            self.qc_manager.log_debug(f"Request {request_id} marked as failed", context="Queue")
        except Exception as e:
            self.qc_manager.log_error(f"Error marking request as failed: {str(e)}", context="Queue")
            raise

    def get_queue_summary(self) -> List[Dict[str, Any]]:
        """
        Get a summary of requests in the queue.

        Returns:
            List[Dict[str, Any]]: List of request summaries
        """
        summary = []
        try:
            for priority, request_id in sorted(self.memory_queue.queue):
                request = self.db_handler.get_request_by_id(request_id)
                if request:
                    summary.append({
                        'id': request_id,
                        'priority': priority,
                        'query': request.get('params', {}).get('query', 'N/A')
                    })
            return summary
        except Exception as e:
            self.qc_manager.log_error(f"Error getting queue summary: {str(e)}", context="Queue")
            raise

    def clear_queue(self) -> None:
        """
        Clear all requests from the queue.
        """
        try:
            while not self.memory_queue.empty():
                _, request_id = self.memory_queue.get()
                self.db_handler.update_request_status(
                    request_id,
                    'cancelled',
                    {'cancelled_at': datetime.utcnow().isoformat()}
                )
            self.qc_manager.log_debug("Queue cleared", context="Queue")
        except Exception as e:
            self.qc_manager.log_error(f"Error clearing queue: {str(e)}", context="Queue")
            raise