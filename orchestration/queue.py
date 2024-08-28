import json
import os
from collections import deque
from datetime import datetime
import hashlib
from masa_tools.qc.qc_manager import QCManager

class Queue:
    def __init__(self, file_path, state_manager):
        """
        Initialize the Queue.

        :param file_path: The file path for the queue.
        :param state_manager: The StateManager instance for managing request states.
        """
        self.file_path = file_path
        self.memory_queue = deque()
        self.request_data = {}
        self.qc_manager = QCManager()
        self.state_manager = state_manager
        self._load_queue()

    def _load_queue(self):
        """
        Load the queue from the file and sort it by the creation date of the requests.
        """
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                self.request_data = data['requests']
                # Sort the queue by the creation date of the requests
                sorted_queue = sorted(data['queue'], key=lambda req_id: self.request_data[req_id]['created_at'])
                self.memory_queue = deque(sorted_queue)
        else:
            self.request_data = {}
            self.memory_queue = deque()

    def _save_queue(self):
        """
        Save the queue to the file.
        """
        self.qc_manager.log_debug("Saving queue to file", context="Queue")
        with open(self.file_path, 'w') as f:
            json.dump({
                'queue': list(self.memory_queue),
                'requests': self.request_data
            }, f, indent=2)
        self.qc_manager.log_debug(f"Queue saved. Current queue size: {len(self.memory_queue)}", context="Queue")

    def add(self, request):
        """
        Add a request to the queue.

        :param request: The request to add.
        """
        request_id = request['id']
        query = request['params'].get('query', 'N/A')
        current_status = self.request_data.get(request_id, {}).get('status', 'new')
        
        log_message = f"Request: Query '{query}' (ID: {request_id}) "
        
        if current_status == 'completed':
            log_message += "already completed. Not adding to queue."
        elif current_status in ['queued', 'in_progress']:
            log_message += f"is {current_status}. Ensuring it's in the queue."
            if request_id not in self.memory_queue:
                self.memory_queue.append(request_id)
        else:
            log_message += "added to queue."
            self.request_data[request_id] = {
                'request': request,
                'status': 'queued',
                'created_at': datetime.now().isoformat()
            }
            if request_id not in self.memory_queue:
                self.memory_queue.append(request_id)
        
        self.qc_manager.log_info(log_message, context="Queue")
        self._save_queue()
        self.qc_manager.log_debug(f"Queue size after adding request: {len(self.memory_queue)}", context="Queue")

    def get(self):
        """
        Get the next request from the queue.

        :return: The next request or None if the queue is empty.
        """
        if not self.memory_queue:
            self.qc_manager.log_debug("Attempted to get request from empty queue", context="Queue")
            return None

        request_id = self.memory_queue.popleft()
        self.qc_manager.log_debug(f"Getting request {request_id} from queue", context="Queue")
        request_info = self.request_data.get(request_id)
        if request_info:
            request_info['status'] = 'in_progress'
            self._save_queue()
            self.qc_manager.log_debug(f"Request {request_id} removed from queue. New queue size: {len(self.memory_queue)}", context="Queue")
            self.qc_manager.log_debug(f"Updating state for request {request_id} to 'in_progress'", context="Queue")
            self.state_manager.update_request_state(request_id, 'in_progress') 
            return request_info['request']
        else:
            self.qc_manager.log_warning(f"Request {request_id} found in queue but not in request_data", context="Queue")
            return None

    def complete(self, request_id):
        """
        Mark a request as completed and remove it from the queue.

        :param request_id: The ID of the request to mark as completed.
        """
        self.qc_manager.log_debug(f"Marking request {request_id} as completed", context="Queue")
        if request_id in self.request_data:
            self.request_data[request_id]['status'] = 'completed'
            self.memory_queue.remove(request_id) 
            self._save_queue()
            self.qc_manager.log_debug(f"Request {request_id} marked as completed and removed from queue", context="Queue")
        else:
            self.qc_manager.log_warning(f"Request {request_id} not found for completion", context="Queue")

    def fail(self, request_id, error):
        """
        Mark a request as failed and log the error.

        :param request_id: The ID of the request to mark as failed.
        :param error: The error message.
        """
        self.qc_manager.log_debug(f"Marking request {request_id} as failed", context="Queue")
        if request_id in self.request_data:
            self.request_data[request_id]['status'] = 'failed'
            self.request_data[request_id]['error'] = str(error)
            self._save_queue()
            self.qc_manager.log_debug(f"Request {request_id} marked as failed", context="Queue")
            self.state_manager.update_request_state(request_id, 'failed', {'error': str(error)})
        else:
            self.qc_manager.log_warning(f"Request {request_id} not found for failure logging", context="Queue")

    def get_status(self, request_id):
        """
        Get the status of a request.

        :param request_id: The ID of the request.
        :return: The status of the request.
        """
        return self.request_data.get(request_id)

    def get_all_statuses(self):
        """
        Get the statuses of all requests.

        :return: A dictionary containing the statuses of all requests.
        """
        return self.request_data

    def resume_incomplete_requests(self):
        """
        Resume incomplete requests by adding them back to the queue.
        """
        for request_id, request_info in self.request_data.items():
            if request_info['status'] in ['queued', 'in_progress']:
                if request_id not in self.memory_queue:
                    self.memory_queue.append(request_id)
        self._save_queue()

    def clear_queue(self):
        """
        Clear the queue and request data.
        """
        self.memory_queue.clear()
        self.request_data = {}
        self._save_queue()