import threading
import json

class StateManager:
    """
    A utility class for managing state across the application.
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
        """
        try:
            with open(self._state_file, 'r') as file:
                self._state = json.load(file)
        except FileNotFoundError:
            pass

    def _save_state(self):
        """
        Save the state to the file.
        """
        with open(self._state_file, 'w') as file:
            json.dump(self._state, file)

    def set_state(self, key, value):
        """
        Set a state value for the given key.

        :param key: The key to set the state for.
        :type key: str
        :param value: The value to set for the key.
        """
        with self._lock:
            self._state[key] = value
            self._save_state()

    def get_state(self, key, default=None):
        """
        Get the state value for the given key.

        :param key: The key to get the state for.
        :type key: str
        :param default: The default value to return if the key is not found (default is None).
        :return: The state value for the key, or the default value if not found.
        """
        with self._lock:
            return self._state.get(key, default)

    def remove_state(self, key):
        """
        Remove the state value for the given key.

        :param key: The key to remove the state for.
        :type key: str
        """
        with self._lock:
            self._state.pop(key, None)
            self._save_state()

    def clear_state(self):
        """
        Clear all state values.
        """
        with self._lock:
            self._state.clear()
            self._save_state()