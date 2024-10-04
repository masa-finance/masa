"""
State Manager module for the MASA project.

This module provides the StateManager class, which is responsible for
managing the state of requests throughout their lifecycle in the MASA system.

The StateManager class handles the state transitions of requests and maintains
consistency with the priority queue implementation. It provides methods
for updating, retrieving, and removing request states.

Attributes:
    _state_file (str): File path to store the state data.
    _lock (threading.Lock): Lock for thread-safe operations.
    qc_manager (tools.qc.qc_manager.QCManager): Quality control manager for logging.
    _state (dict): In-memory representation of the current state.
"""

import json
import threading
from pathlib import Path
from datetime import datetime
from ..tools.qc.qc_manager import QCManager
from ..tools.utils.paths import ensure_dir
from typing import Optional, List

class StateManager:
    """
    Class for managing the state of requests.

    This class handles the state transitions of requests and maintains
    consistency with the priority queue implementation. It provides methods
    for updating, retrieving, and removing request states.

    Attributes:
        _state_file (str): File path to store the state data.
        _lock (threading.Lock): Lock for thread-safe operations.
        qc_manager (tools.qc.qc_manager.QCManager): Quality control manager for logging.
        _state (dict): In-memory representation of the current state.
    """

    def __init__(self, state_file: Path):
        """
        Initialize the StateManager.

        :param state_file: File path to store the state data.
        :type state_file: Path
        """
        self._state_file = state_file
        self._lock = threading.Lock()
        self.qc_manager = QCManager()
        
        # Ensure the directory exists
        self._state_file.parent.mkdir(parents=True, exist_ok=True)
        
        self._state = None

    def load_state(self):
        """Load the state data from the state file."""
        self._state = self._load_state()

    def _load_state(self):
        """
        Load the state data from the state file or create a new state if the file doesn't exist.

        Returns:
            dict: Loaded state data or default state if file doesn't exist or is invalid.
        """
        if self._state_file.exists():
            try:
                with self._state_file.open('r') as file:
                    state = json.load(file)
                # Remove any 'null' entries
                if 'requests' in state:
                    state['requests'] = {k: v for k, v in state['requests'].items() if k != 'null'}
                self.qc_manager.log_debug("State file loaded successfully", context="StateManager")
                return state
            except json.JSONDecodeError:
                self.qc_manager.log_warning("Invalid JSON in state file. Creating new state.", context="StateManager")
        else:
            self.qc_manager.log_info("State file not found. Creating new state.", context="StateManager")
        
        # Return default state if file doesn't exist or is invalid
        return {'requests': {}, 'last_updated': datetime.now().isoformat()}

    def _save_state(self):
        """Save the current state data to the state file."""
        self.qc_manager.log_debug("Saving state to file", context="StateManager")
        with self._state_file.open('w') as file:
            json.dump(self._state, file, indent=4)
        self.qc_manager.log_debug("State saved successfully", context="StateManager")

    def update_request_state(self, request_id, status, progress=None, result=None, error=None, request_details=None):
        """
        Update the state of a request.

        Args:
            request_id (str): ID of the request.
            status (str): New status of the request.
            progress (dict, optional): Progress data of the request.
            result (dict, optional): Result data of the request.
            error (str, optional): Error data of the request.
            request_details (dict, optional): Original request data.
        """
        self.qc_manager.log_debug(f"Updating state for request ID: {request_id}, status: {status}", context="StateManager")
        with self._lock:
            current_time = datetime.now().isoformat()
            if request_id not in self._state['requests']:
                self._state['requests'][request_id] = {
                    'status': status,
                    'created_at': current_time,
                    'last_updated': current_time,
                }
            else:
                self._state['requests'][request_id]['status'] = status
                self._state['requests'][request_id]['last_updated'] = current_time

            if request_details:
                request_details_copy = request_details.copy()
                request_details_copy.pop('status', None)
                self._state['requests'][request_id]['request_details'] = request_details_copy

            if progress:
                self._state['requests'][request_id]['progress'] = progress

            if result:
                # Store only the records fetched and API calls count from the result
                result_summary = {
                    'records_fetched': result[2],
                    'api_calls_count': result[1]
                }
                self._state['requests'][request_id]['result'] = result_summary

            self._state['last_updated'] = current_time
            self._save_state()
            self.qc_manager.log_debug(f"State updated and saved for request {request_id}", context="StateManager")

    def get_all_requests_state(self):
        """
        Get the state of all requests.

        Returns:
            dict: A dictionary containing the state of all requests, excluding any 'null' entries.
        """
        with self._lock:
            return {k: v for k, v in self._state['requests'].items() if k != 'null'}

    def get_request_state(self, request_id):
        """
        Get the state of a specific request.

        Args:
            request_id (str): ID of the request.

        Returns:
            dict: State data of the request or an empty dictionary if not found.
        """
        self.qc_manager.log_debug(f"Retrieving state for request ID: {request_id}", context="StateManager")
        with self._lock:
            state = self._state['requests'].get(request_id)
            if state is None:
                self.qc_manager.log_warning(f"No state found for request ID: {request_id}", context="StateManager")
                return {}
            return state.copy()

    def remove_request_state(self, request_id):
        """
        Remove the state of a specific request.

        :param request_id: ID of the request to remove.
        """
        with self._lock:
            self._state['requests'].pop(request_id, None)
            self._state['last_updated'] = datetime.now().isoformat()
            self._save_state()

    def update_request_priority(self, request_id, priority):
        """
        Update the priority of a request.

        :param request_id: ID of the request.
        :param priority: New priority value.
        """
        with self._lock:
            if request_id in self._state['requests']:
                self._state['requests'][request_id]['priority'] = priority
                self._state['requests'][request_id]['last_updated'] = datetime.now().isoformat()
                self._save_state()
                self.qc_manager.log_debug(f"Priority updated for request {request_id}", context="StateManager")
            else:
                self.qc_manager.log_warning(f"Attempt to update priority for non-existent request {request_id}", context="StateManager")

    def request_exists(self, request_id):
        """
        Check if a request with the given ID exists in the state.

        Args:
            request_id (str): ID of the request to check.

        Returns:
            bool: True if the request exists, False otherwise.
        """
        return request_id in self._state['requests']

    def get_active_requests(self):
        """
        Get all requests that are either queued or in progress.

        Returns:
            dict: A dictionary of active requests, keyed by request ID.
        """
        return {
            k: v for k, v in self._state['requests'].items()
            if v.get('status') in ['queued', 'in_progress']
        }

    def clear_requests(self, request_ids: Optional[List[str]] = None) -> None:
        """
        Clear queued or in-progress requests by changing their status to 'cancelled'.

        Args:
            request_ids (List[str], optional): List of request IDs to clear.
                                               If None, clears all queued or in-progress requests.
        """
        with self._lock:
            current_time = datetime.now().isoformat()
            if request_ids is None:
                # Clear all queued or in-progress requests
                for request_id, request_data in self._state['requests'].items():
                    if request_data.get('status') in ['queued', 'in_progress']:
                        request_data['status'] = 'cancelled'
                        request_data['last_updated'] = current_time
            else:
                # Clear specified requests
                for request_id in request_ids:
                    if request_id in self._state['requests']:
                        self._state['requests'][request_id]['status'] = 'cancelled'
                        self._state['requests'][request_id]['last_updated'] = current_time
                    else:
                        self.qc_manager.log_warning(f"Request ID {request_id} not found.", context="StateManager")

            # Update the last_updated timestamp and save the state
            self._state['last_updated'] = current_time
            self._save_state()

    def get_requests_by_status(self, statuses: Optional[List[str]] = None) -> dict:
        """
        Retrieve requests filtered by status.

        Args:
            statuses (List[str], optional): List of statuses to filter by. If None, returns all requests.

        Returns:
            dict: Dictionary of requests matching the specified statuses.
        """
        with self._lock:
            if statuses is None:
                return self._state['requests'].copy()
            else:
                return {
                    request_id: data
                    for request_id, data in self._state['requests'].items()
                    if data.get('status') in statuses
                }