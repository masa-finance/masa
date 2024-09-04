"""
State Manager module for the MASA project.

This module provides the StateManager class, which is responsible for
managing the state of requests throughout their lifecycle in the MASA system.
"""

import json
import os
import threading
from datetime import datetime
from tools.qc.qc_manager import QCManager

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

    def __init__(self, state_file):
        """
        Initialize the StateManager.

        Args:
            state_file (str): File path to store the state data.
        """
        self._state_file = state_file
        self._lock = threading.Lock()
        self.qc_manager = QCManager()
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self._state_file), exist_ok=True)
        
        self._state = None

    def load_state(self):
        """
        Load the state data from the state file.
        """
        self._state = self._load_state()

    def _load_state(self):
        """
        Load the state data from the state file or create a new state if the file doesn't exist.

        :return: Loaded state data or default state if file doesn't exist or is invalid.
        """
        if os.path.exists(self._state_file):
            try:
                with open(self._state_file, 'r') as file:
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
        """
        Save the current state data to the state file.
        """
        self.qc_manager.log_debug("Saving state to file", context="StateManager")
        with open(self._state_file, 'w') as file:
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

            if progress is not None:
                self._state['requests'][request_id]['progress'] = progress
            elif status == 'completed':
                self._state['requests'][request_id]['result'] = result
                self._state['requests'][request_id].pop('progress', None)
            elif status == 'failed':
                self._state['requests'][request_id]['error'] = error
                self._state['requests'][request_id].pop('progress', None)

            self._state['last_updated'] = current_time
            self._save_state()
            self.qc_manager.log_debug(f"State updated and saved for request {request_id}", context="StateManager")

    def get_all_requests_state(self):
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