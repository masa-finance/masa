import os
import hashlib
import json
from datetime import datetime
from .request_router import RequestRouter
from .queue import Queue
from .state_manager import StateManager
from masa_tools.qc.logging import Logger
import tqdm
import time

class RequestManager:
    """
    The RequestManager class is responsible for managing and processing requests.

    It interacts with the RequestRouter, Queue, and StateManager to handle request
    routing, queueing, and state management.
    """

    def __init__(self, config, queue_file=None, state_file=None):
        """
        Initialize the RequestManager.

        :param config: The configuration for the RequestManager.
        :param queue_file: (Optional) The file path for the request queue.
        :param state_file: (Optional) The file path for the state manager.
        """
        self.config = config
        self.logger = Logger(__name__)

        orchestration_dir = os.path.dirname(os.path.abspath(__file__))
        self.queue_file = queue_file or os.path.join(orchestration_dir, 'request_queue.json')
        self.state_file = state_file or os.path.join(orchestration_dir, 'state_manager.json')

        self.queue = Queue(self.queue_file)
        self.state_manager = StateManager(self.state_file)
        self.request_router = RequestRouter(self.logger, self.config, self.state_manager)

    def prompt_user_for_queue_action(self, request_list_file=None):
        """
        Prompt the user for action on the existing queue.

        This method logs the current state of the queue and prompts the user
        to decide whether to continue with the existing requests or clear the queue.

        :param request_list_file: (Optional) The file path for the new requests to add.
        """
        in_progress_requests = self._get_in_progress_requests()
        if self.queue.memory_queue or in_progress_requests:
            self.logger.log_info("Existing requests in the queue:")
            for request_id in self.queue.memory_queue:
                request_info = self.state_manager.get_request_state(request_id)
                request_params = request_info.get('original_request', {}).get('params', {})
                request_query = request_params.get('query', 'N/A')
                self.logger.log_info(
                    f"Request ID: {request_id}, Status: {request_info.get('status')}, "
                    f"Created At: {request_info.get('created_at')}, Query: {request_query}"
                )
            
            for request in in_progress_requests:
                request_id = request['id']
                request_info = self.state_manager.get_request_state(request_id)
                request_params = request_info.get('original_request', {}).get('params', {})
                request_query = request_params.get('query', 'N/A')
                self.logger.log_info(
                    f"Request ID: {request_id}, Status: {request_info.get('status')}, "
                    f"Created At: {request_info.get('created_at')}, Query: {request_query}"
                )

            user_input = input("Do you want to continue with these requests? (yes/no): ").strip().lower()
            if user_input == 'no':
                # Clear the queue and update the status of all requests to 'cancelled'
                self.queue.clear_queue()
                self.logger.log_info("Queue has been cleared. Adding new requests from file.")
                
                for request_id in self.queue.memory_queue:
                    self.state_manager.update_request_state(request_id, 'cancelled')
                
                for request in in_progress_requests:
                    request_id = request['id']
                    self.state_manager.update_request_state(request_id, 'cancelled')

                if request_list_file:
                    self.add_requests_from_file(request_list_file)
            else:
                self.logger.log_info("Continuing with existing requests.")
                if request_list_file:
                    self.add_requests_from_file(request_list_file, check_existing=True)
        else:
            self.logger.log_info("No existing requests in the queue. Adding new requests from file.")
            if request_list_file:
                self.add_requests_from_file(request_list_file)

    def add_requests_from_file(self, request_list_file, check_existing=False):
        """
        Add requests from a file to the queue.

        :param request_list_file: The file path for the new requests to add.
        :param check_existing: Whether to check for existing requests in the queue.
        """
        with open(request_list_file, 'r') as file:
            requests = json.load(file)
            for request in requests:
                if check_existing:
                    request_id = self._generate_request_id(request)
                    if self.state_manager.get_request_state(request_id):
                        self.logger.log_info(f"Request {request_id} already exists in the queue. Skipping.")
                        continue
                self.add_request(request)

    def process_requests(self, request_list_file=None):
        """
        Process all requests in the queue.

        It first processes any in-progress requests and then processes new requests
        from the queue until the queue is empty.

        :param request_list_file: (Optional) The file path for the new requests to add.
        """
        # Ensure user is prompted before processing requests
        self.prompt_user_for_queue_action(request_list_file)

        in_progress_requests = self._get_in_progress_requests()
        for request in in_progress_requests:
            self._process_single_request(request)

        while True:
            request = self.queue.get()
            if not request:
                break
            self._process_single_request(request)

    def _generate_request_id(self, request):
        """
        Generate a unique request ID based on the request content.

        :param request: The request dictionary.
        :return: The generated request ID.
        """
        request_copy = request.copy()
        request_copy.pop('id', None)
        request_json = json.dumps(request_copy, sort_keys=True).encode('utf-8')
        return hashlib.sha256(request_json).hexdigest()

    def add_request(self, request):
        """
        Add a new request to the queue.

        :param request: The request dictionary to add.
        """
        request_id = self._generate_request_id(request)
        request['id'] = request_id

        existing_status = self.state_manager.get_request_state(request_id)
        if existing_status:
            if existing_status.get('status') == 'completed':
                self.logger.log_info(f"Request {request_id} already completed. Skipping.")
                return
            elif existing_status.get('status') == 'in_progress':
                self.logger.log_info(f"Request {request_id} is already in progress. It will be resumed.")
                return

        self.queue.add(request)
        self.state_manager.update_request_state(request_id, 'queued', original_request=request)
        self.logger.log_info(f"Added request {request_id} to queue")

    def _get_in_progress_requests(self):
        """
        Get all requests that are currently in progress.

        :return: A list of in-progress requests.
        """
        all_requests = self.state_manager.get_all_requests_state()
        return [
            request['original_request']
            for request in all_requests.values()
            if request.get('status') == 'in_progress' and 'original_request' in request
        ]

    def _process_single_request(self, request):
        """
        Process a single request.

        :param request: The request dictionary to process.
        """
        request_id = request['id']
        self.logger.log_info(f"Processing request {request_id}")
        try:
            self.state_manager.update_request_state(request_id, 'in_progress', original_request=request)
            self.request_router.route_request(request)
            self.queue.complete(request_id)
            self.state_manager.update_request_state(request_id, 'completed', original_request=request)
            self.logger.log_info(f"Completed request {request_id}")
        except Exception as e:
            error_info = {
                'type': type(e).__name__,
                'message': str(e),
                'request_id': request_id
            }
            self.logger.log_error(error_info)
            self.queue.fail(request_id, str(e))
            self.state_manager.update_request_state(request_id, 'failed', progress={'error': str(e)}, original_request=request)
            
            # Create a progress bar for retry delay
            retry_delay = self.config.get('retry_delay', 60)  # Get the retry delay from the config or default to 60 seconds
            for _ in tqdm.tqdm(range(retry_delay), desc=f"Retrying request {request_id} in", unit="s", leave=False):
                time.sleep(1)
            
            # Retry the request
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
        all_requests_state = self.state_manager.get_all_requests_state()
        pretty_requests_status = []

        for request_id, request_state in all_requests_state.items():
            pretty_request_status = {
                'request_id': request_id,
                'status': request_state['status'],
                'created_at': request_state['created_at'],
                'last_updated': request_state['last_updated'],
                'query': request_state['original_request']['params'].get('query', 'N/A'),
                'count': request_state['original_request']['params'].get('count', 'N/A'),
                'retriever': request_state['original_request'].get('retriever', 'N/A'),
                'endpoint': request_state['original_request'].get('endpoint', 'N/A'),
                'progress': request_state.get('progress', {})
            }
            pretty_requests_status.append(pretty_request_status)

        return pretty_requests_status

    def resume_incomplete_requests(self):
        """
        Resume any incomplete requests in the queue.
        """
        self.queue.resume_incomplete_requests()