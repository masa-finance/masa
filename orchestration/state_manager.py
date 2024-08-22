import json
import threading
from datetime import datetime

class StateManager:
    def __init__(self, state_file):
        self._state_file = state_file
        self._lock = threading.Lock()
        self._state = self._load_state()

    def _load_state(self):
        try:
            with open(self._state_file, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {'requests': {}, 'last_updated': datetime.now().isoformat()}

    def _save_state(self):
        with open(self._state_file, 'w') as file:
            json.dump(self._state, file, indent=4)

    def update_request_state(self, request_id, status, progress=None, original_request=None):
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
                self._state['requests'][request_id].update({
                    'status': status,
                    'progress': progress or self._state['requests'][request_id].get('progress', {}),
                    'last_updated': datetime.now().isoformat()
                })
                if original_request:
                    self._state['requests'][request_id]['original_request'] = original_request
            self._state['last_updated'] = datetime.now().isoformat()
            self._save_state()

    def get_request_state(self, request_id):
        with self._lock:
            return self._state['requests'].get(request_id, {})

    def get_all_requests_state(self):
        with self._lock:
            return self._state['requests']

    def remove_request_state(self, request_id):
        with self._lock:
            self._state['requests'].pop(request_id, None)
            self._state['last_updated'] = datetime.now().isoformat()
            self._save_state()