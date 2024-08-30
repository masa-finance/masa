"""
Queue module for the MASA project.

This module provides a priority queue implementation for managing requests
in the MASA system, ensuring efficient processing based on request priorities.

The Queue class uses Python's built-in PriorityQueue to manage requests with priorities.
Lower priority values indicate higher priority.

Attributes:
    memory_queue (queue.PriorityQueue): The in-memory priority queue.
    request_data (dict): A dictionary to store request data.
    qc_manager (tools.qc.qc_manager.QCManager): Quality control manager for logging.
    state_manager (orchestration.state_manager.StateManager): Manager for handling request states.
"""

import json
import os
from queue import PriorityQueue
from datetime import datetime
from tools.qc.qc_manager import QCManager

class Queue:
    """
    A priority queue implementation for managing requests.

    This class uses Python's built-in PriorityQueue to manage requests with priorities.
    Lower priority values indicate higher priority.

    Attributes:
        memory_queue (queue.PriorityQueue): The in-memory priority queue.
        request_data (dict): A dictionary to store request data.
        qc_manager (tools.qc.qc_manager.QCManager): Quality control manager for logging.
        state_manager (orchestration.state_manager.StateManager): Manager for handling request states.
    """

    def __init__(self, state_manager, queue_file):
        """
        Initialize the Queue.

        Args:
            state_manager (orchestration.state_manager.StateManager): The StateManager instance for managing request states.
            queue_file (str): File path to store the queue data.
        """
        self.memory_queue = PriorityQueue()
        self.state_manager = state_manager
        self.qc_manager = QCManager()
        self._queue_file = queue_file
        
        
        os.makedirs(os.path.dirname(self._queue_file), exist_ok=True)
        
        self._load_queue()

    def _load_queue(self):
        """
        Load the queue data from the queue file or create a new queue if the file doesn't exist.
        """
        if os.path.exists(self._queue_file):
            try:
                with open(self._queue_file, 'r') as file:
                    queue_data = json.load(file)
                for priority, request_id in queue_data:
                    self.memory_queue.put((priority, request_id))
                self.qc_manager.log_debug("Queue file loaded successfully", context="Queue")
            except json.JSONDecodeError:
                self.qc_manager.log_warning("Invalid JSON in queue file. Creating new queue.", context="Queue")
                self._save_queue()
        else:
            self.qc_manager.log_info("Queue file not found. Creating new queue.", context="Queue")
            self._save_queue()
        
        self._load_queue_from_state()

    def _save_queue(self):
        """
        Save the current queue data to the queue file.
        """
        self.qc_manager.log_debug("Saving queue to file", context="Queue")
        queue_data = list(self.memory_queue.queue)
        with open(self._queue_file, 'w') as file:
            json.dump(queue_data, file, indent=4)
        self.qc_manager.log_debug("Queue saved successfully", context="Queue")

    def _load_queue_from_state(self):
        """
        Load queued and in-progress requests from the state manager into the queue.
        """
        all_requests = self.state_manager.get_all_requests_state()
        for request_id, request_state in all_requests.items():
            if request_state.get('status') in ['queued', 'in_progress']:
                request_details = request_state.get('request_details')
                if request_details:
                    self.add(request_details)
        self.qc_manager.log_debug(f"Loaded {self.memory_queue.qsize()} requests from state manager", context="Queue")
        self.qc_manager.log_info(f"Loaded {self.memory_queue.qsize()} requests from state manager", context="Queue")

    def add(self, request):
        """
        Add a request to the queue if it's not already completed or cancelled.

        Args:
            request (dict): The request to add to the queue.
        """
        request_id = request['id']
        current_state = self.state_manager.get_request_state(request_id)
        current_status = current_state.get('status', 'unknown')
        
        # Don't add completed or cancelled requests to the queue
        if current_status in ['completed', 'cancelled']:
            self.qc_manager.log_debug(f"Skipping {current_status} request {request_id}", context="Queue")
            return
        
        priority = request.get('priority', 100)
        self.memory_queue.put((priority, request_id))
        self.qc_manager.log_debug(f"Added request {request_id} with priority {priority} and status {current_status}", context="Queue")
        self._save_queue()

    def get(self):
        """
        Get the next request from the queue.

        Returns:
            dict: The next request, or None if the queue is empty.
        """
        if self.memory_queue.empty():
            self.qc_manager.log_debug("Attempted to get request from empty queue", context="Queue")
            return None

        _, request_id = self.memory_queue.get()
        current_state = self.state_manager.get_request_state(request_id)
        
        if current_state:
            self.qc_manager.log_debug(f"Retrieved request {request_id} from queue. Current status: {current_state.get('status', 'unknown')}", context="Queue")
            self._save_queue()
            return current_state.get('request_details')
        else:
            self.qc_manager.log_warning(f"Request {request_id} not found in state manager", context="Queue")
            return None

    def complete(self, request_id):
        """
        Mark a request as completed and remove it from the queue.

        Args:
            request_id (str): The ID of the request to mark as completed.
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

        Args:
            request_id (str): The ID of the request to mark as failed.
            error (str): The error message.
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

        Args:
            request_id (str): The ID of the request.

        Returns:
            dict: The status of the request.
        """
        return self.request_data.get(request_id)

    def get_all_statuses(self):
        """
        Get the statuses of all requests.

        Returns:
            dict: A dictionary containing the statuses of all requests.
        """
        return self.request_data

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
        return self.request_data.get(request_id, {}).get('request')

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