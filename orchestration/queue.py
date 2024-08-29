import json
from queue import PriorityQueue
from datetime import datetime
from masa_tools.qc.qc_manager import QCManager

class Queue:
    """
    A priority queue implementation for managing requests.

    This class uses Python's built-in PriorityQueue to manage requests with priorities.
    Lower priority values indicate higher priority.

    Attributes:
        memory_queue (PriorityQueue): The in-memory priority queue.
        request_data (dict): A dictionary to store request data.
        qc_manager (QCManager): Quality control manager for logging.
        state_manager (StateManager): Manager for handling request states.
    """

    def __init__(self, state_manager):
        """
        Initialize the Queue.

        :param state_manager: The StateManager instance for managing request states.
        """
        self.memory_queue = PriorityQueue()
        self.state_manager = state_manager
        self.qc_manager = QCManager()
        self._load_queue_from_state()

    def _load_queue_from_state(self):
        all_requests = self.state_manager.get_all_requests_state()
        for request_id, request_state in all_requests.items():
            if request_state.get('status') in ['queued', 'in_progress']:
                original_request = request_state.get('original_request')
                if original_request:
                    self.add(original_request)
        self.qc_manager.log_debug(f"Loaded {self.memory_queue.qsize()} requests from state manager", context="Queue")
        self.qc_manager.log_info(f"Loaded {self.memory_queue.qsize()} requests from state manager", context="Queue")

    def add(self, request):
        """
        Add a request to the queue.
        """
        request_id = request['id']
        current_state = self.state_manager.get_request_state(request_id)
        current_status = current_state.get('status', 'unknown')
        
        # Don't add completed requests to the queue
        if current_status in ['completed', 'cancelled']:
            self.qc_manager.log_debug(f"Skipping {current_status} request {request_id}", context="Queue")
            return
        
        priority = request.get('priority', 100)
        self.memory_queue.put((priority, request_id))
        self.qc_manager.log_debug(f"Added request {request_id} with priority {priority} and status {current_status}", context="Queue")

    def get(self):
        """
        Get the next request from the queue.

        :return: The next request or None if the queue is empty.
        """
        if self.memory_queue.empty():
            self.qc_manager.log_debug("Attempted to get request from empty queue", context="Queue")
            return None

        _, request_id = self.memory_queue.get()
        current_state = self.state_manager.get_request_state(request_id)
        
        if current_state:
            self.qc_manager.log_debug(f"Retrieved request {request_id} from queue. Current status: {current_state.get('status', 'unknown')}", context="Queue")
            return current_state.get('original_request')
        else:
            self.qc_manager.log_warning(f"Request {request_id} not found in state manager", context="Queue")
            return None

    def complete(self, request_id):
        """
        Mark a request as completed and remove it from the queue.

        :param request_id: The ID of the request to mark as completed.
        """
        self.qc_manager.log_debug(f"Marking request {request_id} as completed", context="Queue")
        if request_id in self.request_data:
            self.request_data[request_id]['status'] = 'completed'
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

    def clear_queue(self):
        """
        Clear the queue and request data.
        """
        while not self.memory_queue.empty():
            self.memory_queue.get()
        self.request_data = {}

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