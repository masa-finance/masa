"""
State Manager module for the MASA project.

This module provides the StateManager class, which is responsible for
managing the state of requests throughout their lifecycle in the MASA system.

The StateManager class handles the state transitions of requests and maintains
consistency with the database implementation. It provides methods
for updating, retrieving, and removing request states.

Attributes:
    _lock (threading.Lock): Lock for thread-safe operations.
    qc_manager (tools.qc.qc_manager.QCManager): Quality control manager for logging.
    db_handler (AbstractDatabaseHandler): Database handler for persistent storage.
"""

from typing import Optional, List, Dict, Any
from ..tools.qc.qc_manager import QCManager
from ..tools.database.abstract_database_handler import AbstractDatabaseHandler

class StateManager:
    """
    StateManager acts as an adapter between the application and database layer.
    
    This class provides backward compatibility while delegating actual storage
    operations to the database handler.

    Attributes:
        database (AbstractDatabaseHandler): Database handler for persistent storage
        qc_manager (QCManager): Quality control manager for logging
    """

    def __init__(self, database_handler: AbstractDatabaseHandler):
        """
        Initialize StateManager with database handler.

        Args:
            database_handler (AbstractDatabaseHandler): Database handler instance
        """
        self.database = database_handler
        self.qc_manager = QCManager()

    def update_request_state(self, request_id: str, status: str, **kwargs) -> None:
        """
        Update request state in database.

        Args:
            request_id (str): Request identifier
            status (str): New status
            **kwargs: Additional state information including:
                     request_details (dict): Original request data
                     result (dict): Request processing result
                     error (str): Error message if failed
        """
        progress = {
            'request_details': kwargs.get('request_details', {}),
            'result': kwargs.get('result', {}),
            'error': kwargs.get('error', None)
        }
        self.database.update_request_status(request_id, status, progress)

    def get_request_state(self, request_id: str) -> Dict[str, Any]:
        """
        Get request state from database.

        Args:
            request_id (str): Request identifier

        Returns:
            Dict[str, Any]: Request state including status and details
        """
        return self.database.get_request_by_id(request_id)

    def request_exists(self, request_id: str) -> bool:
        """
        Check if request exists in database.

        Args:
            request_id (str): Request identifier

        Returns:
            bool: True if request exists
        """
        return bool(self.database.get_request_by_id(request_id))

    def get_all_requests_state(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all requests from database.

        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of all requests
        """
        requests = self.database.get_all_requests()
        return {req['request_id']: req for req in requests}

    def get_requests_by_status(self, statuses: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
        """
        Get requests filtered by status.

        Args:
            statuses (Optional[List[str]]): List of statuses to filter by

        Returns:
            Dict[str, Dict[str, Any]]: Filtered requests
        """
        all_requests = self.get_all_requests_state()
        if not statuses:
            return all_requests
        return {
            req_id: state 
            for req_id, state in all_requests.items() 
            if state.get('status') in statuses
        }

    def clear_requests(self, request_ids: Optional[List[str]] = None) -> None:
        """
        Clear requests by setting their status to 'cancelled'.

        Args:
            request_ids (Optional[List[str]]): List of request IDs to clear
        """
        if request_ids:
            for request_id in request_ids:
                self.database.update_request_status(request_id, 'cancelled', {})
        else:
            all_requests = self.get_all_requests_state()
            for request_id, state in all_requests.items():
                if state.get('status') in ['queued', 'in_progress']:
                    self.database.update_request_status(request_id, 'cancelled', {})