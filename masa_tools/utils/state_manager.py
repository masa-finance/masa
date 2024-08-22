import threading
import json
from datetime import datetime

class StateManager:
    """
    A utility class for managing state across the application.

    This class provides methods to load, save, update, and retrieve the state
    of various requests in the application.

    :param state_file: The path to the file where the state will be saved.
    :type state_file: str
    """

    def __init__(self, state_file):
        """
        Initialize the StateManager instance.

        :param state_file: The file path to save and load the state.
        :type state_file: str
        """
        self._state = {}
        self._lock = threading.Lock()  # Use a lock to ensure thread-safety
        self._state_file = state_file
        self._load_state()

    def _load_state(self):
        """
        Load the state from the file.

        If the file doesn't exist or is not valid JSON, an empty state is created.

        :return: The loaded state or an empty state if the file doesn't exist.
        :rtype: dict
        """
        try:
            with open(self._state_file, 'r') as file:
                self._state = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self._state = {}
        
        # Ensure 'requests' key exists
        if 'requests' not in self._state:
            self._state['requests'] = {}
        
        return self._state

    def _save_state(self):
        """
        Save the current state to the file.

        This method writes the current state to the file specified in the constructor.
        """
        with open(self._state_file, 'w') as file:
            json.dump(self._state, file)

    def update_request_state(self, request_id, status, progress=None):
        """
        Update the state of a specific request.

        :param request_id: The unique identifier of the request.
        :type request_id: str
        :param status: The new status of the request.
        :type status: str
        :param progress: Additional progress information (optional).
        :type progress: dict or None
        """
        with self._lock:
            if request_id not in self._state['requests']:
                self._state['requests'][request_id] = {
                    'status': status,
                    'progress': progress or {},
                    'created_at': datetime.now().isoformat(),
                    'last_updated': datetime.now().isoformat()
                }
            else:
                self._state['requests'][request_id].update({
                    'status': status,
                    'progress': progress or self._state['requests'][request_id].get('progress', {}),
                    'last_updated': datetime.now().isoformat()
                })
            self._state['last_updated'] = datetime.now().isoformat()
            self._save_state()

    def get_request_state(self, request_id):
        """
        Get the state of a specific request.

        :param request_id: The unique identifier of the request.
        :type request_id: str
        :return: The state of the request or an empty dict if not found.
        :rtype: dict
        """
        with self._lock:
            return self._state['requests'].get(request_id, {})

    def get_all_requests_state(self):
        """
        Get the state of all requests.

        :return: A dictionary containing the state of all requests.
        :rtype: dict
        """
        with self._lock:
            return self._state['requests']

    def remove_request_state(self, request_id):
        """
        Remove the state of a specific request.

        :param request_id: The unique identifier of the request to be removed.
        :type request_id: str
        """
        with self._lock:
            self._state['requests'].pop(request_id, None)
            self._state['last_updated'] = datetime.now().isoformat()
            self._save_state()