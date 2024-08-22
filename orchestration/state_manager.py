import json
import threading
from datetime import datetime

class StateManager:
    """
    Class for managing the state of requests.

    :param state_file: File path to store the state data.
    """
    def __init__(self, state_file):
        """
        Initialize the StateManager.

        :param state_file: File path to store the state data.
        """
        self._state_file = state_file
        self._lock = threading.Lock()
        self._state = self._load_state()

    def _load_state(self):
        """
        Load the state data from the state file.

        :return: Loaded state data or default state if file doesn't exist or is invalid.
        """
        try:
            with open(self._state_file, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {'requests': {}, 'last_updated': datetime.now().isoformat()}

    def _save_state(self):
        """
        Save the current state data to the state file.
        """
        with open(self._state_file, 'w') as file:
            json.dump(self._state, file, indent=4)

    def update_request_state(self, request_id, status, progress=None, original_request=None):
        """
        Update the state of a request.

        :param request_id: ID of the request.
        :param status: New status of the request.
        :param progress: Progress data of the request (optional).
        :param original_request: Original request data (optional).
        """
        with self._lock:
            if request_id not in self._state['requests']:
                self._state['requests'][request_id] = {
                    'status': status,
                    'progress': progress or {},
                    'original_request': original_request,
                    'created_at': datetime.now().isoformat(),
                    'last_updated': datetime.now().isoformat()
                }
            else:
                current_state = self._state['requests'][request_id]
                current_state['status'] = status
                if progress:
                    current_state['progress'].update(progress)
                current_state['last_updated'] = datetime.now().isoformat()
                if original_request:
                    current_state['original_request'] = original_request
            self._state['last_updated'] = datetime.now().isoformat()
            self._save_state()

    def get_request_state(self, request_id):
        """
        Get the state of a specific request.

        :param request_id: ID of the request.
        :return: State data of the request or an empty dictionary if not found.
        """
        with self._lock:
            return self._state['requests'].get(request_id, {})

    def get_all_requests_state(self):
        """
        Get the state of all requests.

        :return: Dictionary containing the state data of all requests.
        """
        with self._lock:
            return self._state['requests']

    def remove_request_state(self, request_id):
        """
        Remove the state of a specific request.

        :param request_id: ID of the request to remove.
        """
        with self._lock:
            self._state['requests'].pop(request_id, None)
            self._state['last_updated'] = datetime.now().isoformat()
            self._save_state()