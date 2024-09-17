"""
Queue module for the MASA project.

This module provides a priority queue implementation for managing requests
in the MASA system, ensuring efficient processing based on request priorities.

The Queue class uses Python's built-in PriorityQueue to manage requests with priorities.
Lower priority values indicate higher priority.

Attributes:
    memory_queue (queue.PriorityQueue): The in-memory priority queue.
    qc_manager (tools.qc.qc_manager.QCManager): Quality control manager for logging.
    state_manager (orchestration.state_manager.StateManager): Manager for handling request states.
"""

import json
from pathlib import Path
from queue import PriorityQueue
from datetime import datetime
from masa_ai.tools.qc.qc_manager import QCManager
from masa_ai.tools.utils.paths import ensure_dir

class Queue:
    """
    A priority queue implementation for managing requests.

    This class uses Python's built-in PriorityQueue to manage requests with priorities.
    Lower priority values indicate higher priority.

    Attributes:
        memory_queue (queue.PriorityQueue): The in-memory priority queue.
        qc_manager (masa.tools.qc.qc_manager.QCManager): Quality control manager for logging.
        state_manager (masa.orchestration.state_manager.StateManager): Manager for handling request states.
    """

    def __init__(self, state_manager, queue_file: Path):
        """
        Initialize the Queue.

        :param state_manager: StateManager instance for managing request states.
        :param queue_file: File path to store the queue data.
        :type queue_file: Path
        """
        self._queue_file = queue_file
        self.memory_queue = PriorityQueue()
        self.state_manager = state_manager
        self.qc_manager = QCManager()
        self._queue_file.parent.mkdir(parents=True, exist_ok=True)
        
        ensure_dir(self._queue_file.parent)
        
        self._load_queue_from_state()

    def _load_queue_from_state(self):
        """
        Load queued and in-progress requests from the state manager into the queue.
        """
        active_requests = self.state_manager.get_active_requests()
        for request_id, request_state in active_requests.items():
            request_details = request_state.get('request_details', {})
            priority = request_details.get('priority', 100)
            self.memory_queue.put((priority, request_id))
        self.qc_manager.log_info(f"Loaded {self.memory_queue.qsize()} requests from state manager", context="Queue")

    def _load_queue_file(self):
        """
        Load the queue data from the queue file, avoiding duplicates.
        """
        if self._queue_file.exists():
            try:
                with self._queue_file.open('r') as file:
                    queue_data = json.load(file)
                for priority, request_id in queue_data:
                    if not any(item[1] == request_id for item in self.memory_queue.queue):
                        self.memory_queue.put((priority, request_id))
                self.qc_manager.log_debug("Queue file loaded successfully", context="Queue")
            except json.JSONDecodeError:
                self.qc_manager.log_warning("Invalid JSON in queue file. Creating new queue.", context="Queue")
                self._save_queue()
        else:
            self.qc_manager.log_info("Queue file not found. Creating new queue.", context="Queue")
            self._save_queue()
        
        self.qc_manager.log_info(f"Total requests in queue after loading: {self.memory_queue.qsize()}", context="Queue")

    def _save_queue(self):
        """
        Save the current queue data to the queue file.
        """
        self.qc_manager.log_debug("Saving queue to file", context="Queue")
        queue_data = list(self.memory_queue.queue)
        with self._queue_file.open('w') as file:
            json.dump(queue_data, file, indent=4)
        self.qc_manager.log_debug("Queue saved successfully", context="Queue")

    def add(self, request):
        """
        Add a request to the queue if it's not already completed or cancelled.

        Args:
            request (dict): The request to add to the queue.
        """
        request_id = request['id']
        if not any(item[1] == request_id for item in self.memory_queue.queue):
            priority = request.get('priority', 100)
            self.memory_queue.put((priority, request_id))
            self.state_manager.update_request_state(request_id, 'queued', request_details=request)
            self.qc_manager.log_debug(f"Added request {request_id} with priority {priority}", context="Queue")
        else:
            self.qc_manager.log_debug(f"Skipping duplicate request {request_id}", context="Queue")

    def get(self):
        """
        Get the next request from the queue.

        Returns:
            tuple: A tuple containing (request_id, request_details) or (None, None) if the queue is empty.
        """
        if self.memory_queue.empty():
            return None, None
        priority, request_id = self.memory_queue.get()
        request_state = self.state_manager.get_request_state(request_id)

        if request_id is None or not request_state:
            self.qc_manager.log_warning("Skipping request with missing ID or data", context="Queue")
            return None, None

        self.qc_manager.log_debug(f"Retrieved request {request_id} from queue. Current status: {request_state.get('status', 'unknown')}", context="Queue")
        self._save_queue()
        return request_id, request_state.get('request_details')

    def complete(self, request_id):
        """
        Mark a request as completed and remove it from the queue.

        Args:
            request_id (str): The ID of the request to mark as completed.
        """
        self.qc_manager.log_debug(f"Marking request {request_id} as completed", context="Queue")
        self.state_manager.update_request_state(request_id, 'completed')
        self.qc_manager.log_debug(f"Request {request_id} marked as completed", context="Queue")

    def fail(self, request_id, error):
        """
        Mark a request as failed and log the error.

        Args:
            request_id (str): The ID of the request to mark as failed.
            error (str): The error message.
        """
        self.qc_manager.log_debug(f"Marking request {request_id} as failed", context="Queue")
        self.state_manager.update_request_state(request_id, 'failed', error=str(error))
        self.qc_manager.log_debug(f"Request {request_id} marked as failed", context="Queue")

    def get_status(self, request_id):
        """
        Get the status of a request.

        Args:
            request_id (str): The ID of the request.

        Returns:
            dict: The status of the request.
        """
        return self.state_manager.get_request_state(request_id)

    def get_all_statuses(self):
        """
        Get the statuses of all requests.

        Returns:
            dict: A dictionary containing the statuses of all requests.
        """
        return self.state_manager.get_all_requests_state()

    def clear_queue(self):
        """
        Clear the queue and save the empty state.
        """
        while not self.memory_queue.empty():
            self.memory_queue.get()
        self._save_queue()
        self.qc_manager.log_debug("Queue cleared", context="Queue")

    def peek(self):
        """
        Peek at the next request in the queue without removing it.

        Returns:
            dict: The next request or None if the queue is empty.
        """
        if self.memory_queue.empty():
            return None
        _, request_id = self.memory_queue.queue[0]
        request_state = self.state_manager.get_request_state(request_id)
        return request_state.get('request_details')

    def _generate_request_id(self, request):
        """
        Generate a unique id for a request.

        Args:
            request (dict): The request to generate an ID for.

        Returns:
            str: The generated request ID.
        """
        import hashlib
        import json
        request_json = json.dumps(request, sort_keys=True).encode('utf-8')
        return hashlib.sha256(request_json).hexdigest()

    def get_queue_summary(self):
        """
        Get a summary of the requests in the queue.

        Returns:
            list: A list of dictionaries containing request details.
        """
        summary = []
        for priority, request_id in sorted(self.memory_queue.queue):
            request_state = self.state_manager.get_request_state(request_id)
            request_details = request_state.get('request_details', {})
            summary.append({
                'id': request_id,
                'priority': priority,
                'query': request_details.get('params', {}).get('query', 'N/A')
            })
        return summary