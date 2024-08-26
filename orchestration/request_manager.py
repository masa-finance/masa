import os
import hashlib
import json
from datetime import datetime
from .request_router import RequestRouter
from .queue import Queue
from .state_manager import StateManager
from masa_tools.qc.qc_manager import QCManager
import time
from tqdm import tqdm
import traceback

class RequestManager:
    """
    The RequestManager class is responsible for managing and processing requests.

    It interacts with the RequestRouter, Queue, and StateManager to handle request
    routing, queueing, and state management.
    """

    def __init__(self, config):
        """
        Initialize the RequestManager.

        :param config: The configuration for the RequestManager.
        """
        self.qc_manager = QCManager()
        self.config = config
        self.state_file = os.path.join(os.path.dirname(__file__), 'state_manager.json')
        self.state_manager = StateManager(self.state_file)
        self.request_router = RequestRouter(self.qc_manager, self.state_manager)
        self.queue_file = os.path.join(os.path.dirname(__file__), 'request_queue.json')
        self.queue = Queue(self.queue_file, self.state_manager)

    def prompt_user_for_queue_action(self, request_list_file):
        """
        Prompt the user for an action to take on the request queue.

        :param request_list_file: The path to the JSON file containing the request list.
        """
        request_list = self.load_request_list(request_list_file)
        self.qc_manager.log_info("Existing requests in the queue:", context="RequestManager")
        for request in request_list:
            if request is None:
                self.qc_manager.log_error("Skipping invalid request: None", context="RequestManager")
                continue
            if 'id' not in request:
                request_id = self._generate_request_id(request)
                request['id'] = request_id
            request_id = request['id']
            request_type = request.get('type', 'Unknown')
            request_status = request.get('status', 'Unknown')
            self.qc_manager.log_info(f"Request ID: {request_id}, Type: {request_type}, Status: {request_status}", context="RequestManager")

        action = input("Enter the action to take on the request queue (process/cancel/skip): ")
        if action.lower() == 'process':
            self.process_requests(request_list_file)
        elif action.lower() == 'cancel':
            self.cancel_request_queue(request_list_file)
        elif action.lower() == 'skip':
            self.qc_manager.log_info("Skipping request queue processing.", context="RequestManager")
        else:
            self.qc_manager.log_error("Invalid action. Please enter 'process', 'cancel', or 'skip'.", context="RequestManager")

    def load_request_list(self, request_list_file):
        """
        Load the request list from a JSON file.

        Args:
            request_list_file (str): The path to the JSON file containing the request list.

        Returns:
            list: The loaded request list.
        """
        try:
            with open(request_list_file, 'r') as file:
                request_list = json.load(file)
                return request_list
        except FileNotFoundError:
            self.qc_manager.log_error(f"Request list file not found: {request_list_file}", context="RequestManager")
            return []
        except json.JSONDecodeError as e:
            self.qc_manager.log_error(f"Error decoding request list JSON: {str(e)}", context="RequestManager")
            return []

    def add_requests_from_file(self, request_list_file, check_existing=False):
        """
        Add requests from a file to the queue.

        :param request_list_file: The file path for the new requests to add.
        :param check_existing: Whether to check for existing requests in the queue.
        """
        with open(request_list_file, 'r') as file:
            requests = json.load(file)
            for request in requests:
                if 'id' not in request:
                    request['id'] = self._generate_request_id(request)
                if check_existing:
                    request_id = request['id']
                    if self.state_manager.get_request_state(request_id):
                        self.qc_manager.log_info(f"Request {request_id} already exists in the queue. Skipping.", context="RequestManager")
                        continue
                self.add_request(request)

    def process_requests(self, request_list_file=None):
        """
        Process all requests in the queue.

        It first processes any in-progress requests and then processes new requests
        from the queue until the queue is empty.

        :param request_list_file: (Optional) The file path for the new requests to add.
        """
        self.qc_manager.debug(f"Starting process_requests with file: {request_list_file}", context="RequestManager")
        
        if request_list_file:
            self.qc_manager.debug(f"Loading requests from file: {request_list_file}", context="RequestManager")
            self.add_requests_from_file(request_list_file)

        self.queue.resume_incomplete_requests()
        
        in_progress_requests = self._get_in_progress_requests()
        self.qc_manager.debug(f"Found {len(in_progress_requests)} in-progress requests", context="RequestManager")
        for request in in_progress_requests:
            query = request['params'].get('query', 'N/A')
            self.qc_manager.debug(f"Resuming in-progress request: Query '{query}' (ID: {request['id']})", context="RequestManager")
            self.queue.add(request)

        self.qc_manager.debug(f"Total requests in queue: {len(self.queue.memory_queue)}", context="RequestManager")

        while self.queue.memory_queue:
            request = self.queue.get()
            if not request:
                self.qc_manager.debug("Queue.get() returned None despite non-empty queue", context="RequestManager")
                continue
            query = request['params'].get('query', 'N/A')
            self.qc_manager.debug(f"Processing request: Query '{query}' (ID: {request['id']})", context="RequestManager")
            self._process_single_request(request)

        self.qc_manager.debug("All requests processed", context="RequestManager")

    def _get_in_progress_requests(self):
        all_requests = self.state_manager.get_all_requests_state()
        in_progress = []
        for request_id, request_state in all_requests.items():
            if request_state.get('status') in ['in_progress', 'queued']:
                original_request = request_state.get('original_request')
                if original_request:
                    in_progress.append(original_request)
                else:
                    self.qc_manager.debug(f"Invalid in-progress request state: {request_state}", context="RequestManager")
        self.qc_manager.debug(f"Found {len(in_progress)} in-progress or queued requests", context="RequestManager")
        return in_progress

    def _generate_request_id(self, request):
        """
        Generate a unique request ID based on the request content.

        :param request: The request dictionary.
        :return: The generated request ID.
        """
        request_copy = request.copy()
        request_copy.pop('id', None)  # Remove id if it exists to ensure consistent hashing
        request_json = json.dumps(request_copy, sort_keys=True).encode('utf-8')
        return hashlib.sha256(request_json).hexdigest()

    def add_request(self, request):
        """
        Add a new request to the queue.

        :param request: The request dictionary to add.
        """
        request_id = request['id']
        self.qc_manager.debug(f"Adding request {request_id} to system", context="RequestManager")
        
        self.queue.add(request)
        self.state_manager.update_request_state(request_id, 'queued', original_request=request)
        self.qc_manager.debug(f"Request {request_id} added to queue and state updated", context="RequestManager")

    def _process_single_request(self, request):
        """
        Process a single request.

        :param request: The request dictionary to process.
        """
        request_id = request['id']
        self.qc_manager.debug(f"Processing request {request_id}", context="RequestManager")
        try:
            self.state_manager.update_request_state(request_id, 'in_progress', original_request=request)
            self.qc_manager.debug(f"Updated state for request {request_id} to in_progress", context="RequestManager")
            
            self.qc_manager.debug(f"Routing request {request_id}", context="RequestManager")
            self.request_router.route_request(request)
            
            self.queue.complete(request_id)
            self.state_manager.update_request_state(request_id, 'completed', original_request=request)
            self.qc_manager.debug(f"Request {request_id} completed successfully", context="RequestManager")
        except Exception as e:
            self.qc_manager.debug(f"Error processing request {request_id}: {str(e)}", context="RequestManager")
            self.qc_manager.debug(f"Traceback: {traceback.format_exc()}", context="RequestManager")
            self.queue.fail(request_id, str(e))
            self.state_manager.update_request_state(request_id, 'failed', progress={'error': str(e)}, original_request=request)
            
            retry_delay = self.config.get('retry_delay', 60)
            for _ in tqdm(range(retry_delay), desc=f"Retrying request {request_id} in", unit="s", leave=False):
                time.sleep(1)
            
            self.add_request(request)

    def get_request_status(self, request_id):
        """
        Get the status of a specific request.

        :param request_id: The ID of the request.
        :return: The status of the request.
        """
        return self.state_manager.get_request_state(request_id)

    def get_all_requests_status(self):
        """
        Get the status of all requests in a prettier format.

        :return: A list of dictionaries containing the status of all requests.
        """
        all_requests_status = []
        all_requests = self.state_manager.get_all_requests_state()
        for request_id, request_state in all_requests.items():
            original_request = request_state.get('original_request') or {}
            params = original_request.get('params', {})
            status_entry = {
                'request_id': request_id,
                'status': request_state.get('status', 'Unknown'),
                'retriever': original_request.get('retriever', 'N/A'),
                'endpoint': original_request.get('endpoint', 'N/A'),
                'query': params.get('query', 'N/A'),
                'count': params.get('count', 'N/A'),
                'created_at': request_state.get('created_at', 'N/A'),
                'completed_at': request_state.get('completed_at', 'N/A')
            }
            all_requests_status.append(status_entry)
        return all_requests_status

    def resume_incomplete_requests(self):
        """
        Resume any incomplete requests in the queue.
        """
        self.queue.resume_incomplete_requests()

    def cancel_request_queue(self, request_list_file):
        """
        Cancel all requests in the queue.

        Args:
            request_list_file (str): The path to the JSON file containing the request list.
        """
        request_list = self.load_request_list(request_list_file)
        for request in request_list:
            if request is None:
                self.qc_manager.log_error("Skipping invalid request: None", context="RequestManager")
                continue
            if 'id' not in request:
                self.qc_manager.log_error(f"Skipping request with missing 'id' key: {request}", context="RequestManager")
                continue
            request_id = request['id']
            self.cancel_request(request_id)

    def cancel_request(self, request_id):
        """
        Cancel a specific request.

        Args:
            request_id (str): The ID of the request to cancel.
        """
        request_state = self.state_manager.get_request_state(request_id)
        if request_state:
            self.state_manager.update_request_state(request_id, 'cancelled')
            self.queue.remove(request_id)
            self.qc_manager.log_info(f"Cancelled request {request_id}", context="RequestManager")
        else:
            self.qc_manager.log_warning(f"Request {request_id} not found in the queue", context="RequestManager")