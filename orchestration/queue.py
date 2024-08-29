import json
import os
from queue import PriorityQueue
from datetime import datetime
from masa_tools.qc.qc_manager import QCManager

class Queue:
    """
    A priority queue implementation for managing requests.

    This class uses Python's built-in PriorityQueue to manage requests with priorities.
    Lower priority values indicate higher priority.

    Attributes:
        file_path (str): The file path for persisting the queue.
        memory_queue (PriorityQueue): The in-memory priority queue.
        request_data (dict): A dictionary to store request data.
        qc_manager (QCManager): Quality control manager for logging.
        state_manager (StateManager): Manager for handling request states.
    """

    def __init__(self, file_path, state_manager):
        """
        Initialize the Queue.

        :param file_path: The file path for the queue.
        :param state_manager: The StateManager instance for managing request states.
        """
        self.file_path = file_path
        self.memory_queue = PriorityQueue()
        self.request_data = {}
        self.qc_manager = QCManager()
        self.state_manager = state_manager
        self._load_queue()

    def _load_queue(self):
        """
        Load the queue from the file and reconstruct the priority queue.
        """
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                try:
                    data = json.load(f)
                    self.qc_manager.log_debug(f"Loaded data structure: {list(data.keys())}", context="Queue")
                    
                    if isinstance(data, dict) and 'queue' in data and 'requests' in data:
                        queue_data = data['queue']
                        requests_data = data['requests']
                        
                        for request_id in queue_data:
                            if request_id in requests_data:
                                request = requests_data[request_id]
                                priority = request.get('priority', 100)
                                self.request_data[request_id] = request
                                self.memory_queue.put((priority, request_id))
                            else:
                                self.qc_manager.log_warning(f"Request ID {request_id} found in queue but not in requests", context="Queue")
                        
                        self.qc_manager.log_debug(f"Loaded {len(self.request_data)} requests into the queue", context="Queue")
                    else:
                        self.qc_manager.log_error("Invalid JSON structure in request_queue.json. Expected 'queue' and 'requests' keys.", context="Queue")
                
                except json.JSONDecodeError as e:
                    self.qc_manager.log_error(f"Error decoding JSON from {self.file_path}: {str(e)}", context="Queue")
        else:
            self.qc_manager.log_debug(f"Queue file not found: {self.file_path}", context="Queue")
            self.request_data = {}

    def _save_queue(self):
        """
        Save the queue to the file.
        """
        data = {
            "queue": list(self.request_data.keys()),
            "requests": self.request_data
        }
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=2)
        self.qc_manager.log_debug(f"Queue saved. Current queue size: {self.memory_queue.qsize()}", context="Queue")

    def add(self, request):
        """
        Add a request to the queue.
        """
        if 'id' not in request:
            self.qc_manager.log_warning(f"Request does not have an 'id' key. This should be handled by RequestManager.", context="Queue")
            return

        request_id = request['id']
        priority = request.get('priority', 100)
        
        # Ensure the request has a status, default to 'queued'
        if 'status' not in request:
            request['status'] = 'queued'
        
        self.request_data[request_id] = request
        self.memory_queue.put((priority, request_id))
        self._save_queue()
        self.qc_manager.log_debug(f"Added request {request_id} with priority {priority} and status {request['status']}", context="Queue")

    def get(self):
        """
        Get the next request from the queue.

        :return: The next request or None if the queue is empty.
        """
        if self.memory_queue.empty():
            self.qc_manager.log_debug("Attempted to get request from empty queue", context="Queue")
            return None

        _, request_id = self.memory_queue.get()
        self.qc_manager.log_debug(f"Getting request {request_id} from queue", context="Queue")
        request = self.request_data.get(request_id)
        if request:
            self.qc_manager.log_debug(f"Request {request_id} retrieved from queue. New queue size: {self.memory_queue.qsize()}", context="Queue")
            return request
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
            self._save_queue()
            self.qc_manager.log_debug(f"Request {request_id} marked as completed", context="Queue")
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
        self.qc_manager.log_debug(f"Resuming incomplete requests. Current queue size: {self.memory_queue.qsize()}", context="Queue")
        for request_id, request_info in self.request_data.items():
            self.qc_manager.log_debug(f"Checking request {request_id}: {request_info}", context="Queue")
            
            status = request_info.get('status', 'queued')
            
            if status in ['queued', 'in_progress']:
                if not any(req_id == request_id for _, req_id in self.memory_queue.queue):
                    priority = request_info.get('priority', 100)
                    self.memory_queue.put((priority, request_id))
                    self.qc_manager.log_debug(f"Resumed request {request_id} with status {status}", context="Queue")
                else:
                    self.qc_manager.log_debug(f"Request {request_id} already in queue", context="Queue")
        
        self.qc_manager.log_debug(f"After resuming, queue size: {self.memory_queue.qsize()}", context="Queue")
        self._save_queue()

    def clear_queue(self):
        """
        Clear the queue and request data.
        """
        while not self.memory_queue.empty():
            self.memory_queue.get()
        self.request_data = {}
        self._save_queue()

    def peek(self):
        """
        Peek at the next request in the queue without removing it.

        :return: The next request or None if the queue is empty.
        """
        if self.memory_queue.empty():
            return None
        _, request_id = self.memory_queue.queue[0]
        return self.request_data.get(request_id, {}).get('request')

    def _generate_request_id(self, request):
        """Generate a unique id for a request."""
        import hashlib
        import json
        request_json = json.dumps(request, sort_keys=True).encode('utf-8')
        return hashlib.sha256(request_json).hexdigest()