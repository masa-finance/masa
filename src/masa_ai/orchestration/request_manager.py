"""
Request Manager module for the MASA project.

This module provides the RequestManager class, which is responsible for
orchestrating the overall request processing workflow in the MASA system.

The RequestManager class manages the lifecycle of requests, including queueing,
routing, processing, and state management. It integrates various components of 
the MASA system to ensure efficient and reliable request handling.

Attributes:
    qc_manager (tools.qc.qc_manager.QCManager): Quality control manager for logging and error handling.
    config (dict): Configuration settings for the request manager.
    state_manager (orchestration.state_manager.StateManager): Manager for handling request states.
    request_router (orchestration.request_router.RequestRouter): Router for directing requests to appropriate handlers.
    queue (orchestration.queue.Queue): Priority queue for managing requests.
"""

import hashlib
import json
from pathlib import Path
from typing import Optional, List
from masa_ai.orchestration.request_router import RequestRouter
from masa_ai.orchestration.queue import Queue
from masa_ai.orchestration.state_manager import StateManager
from ..tools.qc.qc_manager import QCManager
from ..configs.config import global_settings
from ..tools.utils.paths import ensure_dir, ORCHESTRATION_DIR

class RequestManager:
    """
    RequestManager class for orchestrating request processing.
    """
    def __init__(self):
        """
        Initialize the RequestManager.
        """
        self.qc_manager = QCManager()
        self.config = global_settings
        self.state_file = ORCHESTRATION_DIR / "request_manager_state.json"
        self.queue_file = ORCHESTRATION_DIR / "request_queue.json"
        
        # Ensure directories exist
        ensure_dir(self.state_file.parent)
        ensure_dir(self.queue_file.parent)
        
        self.state_manager = StateManager(self.state_file)
        self.request_router = RequestRouter(self.qc_manager, self.state_manager)
        self.queue = None

    def process_requests(self, requests: Optional[list] = None):
        """
        Process requests from a file or the existing queue.

        This method is the main entry point for request processing. It loads
        requests from a file if provided, otherwise processes requests from
        the existing queue.

        Args:
            requests (list, optional): List of requests to process. If None, process the existing queue.
        """
        
        self.state_manager.load_state()

        if requests:
            self._update_state_with_requests(requests)

        self.queue = Queue(self.state_manager, self.queue_file)

        # Process the requests
        self._process_queue()

    def _update_state_with_requests(self, requests: list):
        """
        Update the state manager with new requests.

        Args:
            requests (list): List of requests.
        """
        self.qc_manager.log_debug("Updating state with new requests", context="RequestManager")
        for request in requests:
            request_id = self._generate_request_id(request)
            if not self.state_manager.request_exists(request_id):
                self.state_manager.update_request_state(request_id, 'queued', request_details=request)
        self.qc_manager.log_info("Updated state with new requests")

    def _process_queue(self):
        """
        Process requests from the queue.
        """
        queue_summary = self.queue.get_queue_summary()
        self.qc_manager.log_info("Queue Summary:")
        for item in queue_summary:
            self.qc_manager.log_info(f"ID: {item['id']}, Priority: {item['priority']}, Query: {item['query']}")

        total_requests = len(queue_summary)
        self.qc_manager.log_info(f"Starting to process {total_requests} requests")

        processed_requests = 0
        while True:
            request_id, request = self.queue.get()
            if request_id is None:
                break

            processed_requests += 1
            self.qc_manager.log_info(f"Processing request {processed_requests} of {total_requests}", context="RequestManager")

            try:
                self._process_single_request(request_id, request)
            except Exception as e:
                self.qc_manager.log_error(f"Error processing request: {str(e)}", context="RequestManager")

        self.qc_manager.log_info(f"Completed processing all {total_requests} requests")

    def _process_single_request(self, request_id, request):
        """
        Process a single request.

        Args:
            request_id (str): The ID of the request.
            request (dict): The request to process.

        Raises:
            Exception: If an error occurs during request processing.
        """
        try:
            current_state = self.state_manager.get_request_state(request_id)
        except KeyError:
            self.qc_manager.log_error(f"Request {request_id} not found in the state manager", context="RequestManager")
            return

        self.qc_manager.log_debug(f"Processing request {request_id}, Current status: {current_state['status']}", context="RequestManager")

        if current_state['status'] != 'in_progress':
            self.state_manager.update_request_state(request_id, 'in_progress', request_details=request)

        try:
            result = self.request_router.route_request(request_id, request)
            self.state_manager.update_request_state(request_id, 'completed', result=result, request_details=request)
            self.qc_manager.log_info(f"Request completed: {request_id}")
        except Exception as e:
            self.qc_manager.log_error(f"Error in request {request_id}: {str(e)}")
            self.state_manager.update_request_state(request_id, 'failed', error=str(e), request_details=request)
            raise

    def _generate_request_id(self, request):
        """
        Generate a unique request ID based on the request content.

        Args:
            request (dict): The request dictionary.

        Returns:
            str: The generated request ID.
        """
        request_copy = request.copy()
        request_copy.pop('id', None) 
        request_json = json.dumps(request_copy, sort_keys=True).encode('utf-8')
        return hashlib.sha256(request_json).hexdigest()

    def prompt_user_for_queue_action(self, request_list_file):
        """
        Prompt the user for an action to take on the request queue.

        Args:
            request_list_file (str): Path to the JSON file containing requests.
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

    def load_request_list(self, request_list_file: str) -> list:
        """
        Load the request list from a JSON file.

        Args:
            request_list_file (str): Path to the JSON file containing requests.

        Returns:
            list: The loaded request list.
        """
        try:
            request_list_path = Path(request_list_file)
            with request_list_path.open('r') as file:
                request_list = json.load(file)
                return request_list
        except FileNotFoundError:
            self.qc_manager.log_error(f"Request list file not found: {request_list_file}", context="RequestManager")
            return []
        except json.JSONDecodeError as e:
            self.qc_manager.log_error(f"Error decoding request list JSON: {str(e)}", error_info=e, context="RequestManager")
            return []

    def _get_in_progress_requests(self):
        """
        Get the requests that are currently in progress or queued.

        Returns:
            list: The list of in-progress or queued requests.
        """
        all_requests = self.state_manager.get_all_requests_state()
        in_progress = []
        for request_id, request_state in all_requests.items():
            if request_state.get('status') in ['in_progress', 'queued']:
                original_request = request_state.get('original_request')
                if original_request:
                    in_progress.append(original_request)
                else:
                    self.qc_manager.log_debug(f"Invalid in-progress request state: {request_state}", context="RequestManager")
        self.qc_manager.log_debug(f"Found {len(in_progress)} in-progress or queued requests", context="RequestManager")
        return in_progress

    def add_request(self, request):
        """
        Add a request to the system.

        Args:
            request (dict): The request to add.
        """
        
        request_id = request['id']
        self.qc_manager.log_debug(f"Adding request {request_id} to system", context="RequestManager")
        
        self.queue.add(request)
        self.state_manager.update_request_state(request_id, 'queued', request_details=request)
        self.qc_manager.log_debug(f"Request {request_id} added to queue and state updated", context="RequestManager")

    def get_request_status(self, request_id):
        """
        Get the status of a request.

        Args:
            request_id (str): The ID of the request.

        Returns:
            dict: The status of the request.
        """
        return self.state_manager.get_request_state(request_id)

    def get_all_requests_status(self):
        """
        Get the status of all requests.

        Returns:
            list: A list of dictionaries containing the status of all requests.
        """
        all_requests_status = []
        all_requests = self.state_manager.get_all_requests_state()
        for request_id, request_state in all_requests.items():
            request_details = request_state.get('request_details', {})
            params = request_details.get('params', {})
            status_entry = {
                'request_id': request_id,
                'status': request_state.get('status', 'Unknown'),
                'scraper': request_details.get('scraper', 'N/A'),
                'endpoint': request_details.get('endpoint', 'N/A'),
                'query': params.get('query', 'N/A'),
                'count': params.get('count', 'N/A'),
                'created_at': request_state.get('created_at', 'N/A'),
                'completed_at': request_state.get('completed_at', 'N/A')
            }
            all_requests_status.append(status_entry)
        return all_requests_status

    def resume_incomplete_requests(self):
        """
        Resume incomplete requests (in progress, queued, or failed).
        """
        all_requests = self.state_manager.get_all_requests_state()
        for request_id, request_state in all_requests.items():
            if request_state.get('status') in ['in_progress', 'queued', 'failed']:
                original_request = request_state.get('original_request')
                if original_request:
                    self.add_request(original_request)
                else:
                    self.qc_manager.log_debug(f"Invalid in-progress request state: {request_state}", context="RequestManager")
        self.qc_manager.log_debug(f"Resumed incomplete requests. Current queue size: {len(self.queue)}", context="RequestManager")

    def cancel_request_queue(self, request_list_file):
        """
        Cancel the requests in the queue based on the provided request list file.

        Args:
            request_list_file (str): Path to the JSON file containing requests to cancel.
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
            self.qc_manager.log_info(f"Cancelled request {request_id}", context="RequestManager")
        else:
            self.qc_manager.log_warning(f"Request {request_id} not found in the state manager", context="RequestManager")

    def list_requests(self, statuses: Optional[List[str]] = None):
        """
        List requests with their ID, status, query, and last updated time.

        Args:
            statuses (List[str], optional): List of statuses to filter requests.
                                            If None, lists all requests.
        """
        self.qc_manager.log_debug("Listing requests", context="RequestManager")
        self.state_manager.load_state()
        requests = self.state_manager.get_requests_by_status(statuses)
        
        if not requests:
            self.qc_manager.log_info("No requests found.", context="RequestManager")
            return

        # Collect all request details in a single message
        messages = []
        for request_id, request_state in requests.items():
            status = request_state.get('status', 'Unknown')
            last_updated = request_state.get('last_updated', 'N/A')
            query = request_state.get('request_details', {}).get('params', {}).get('query', 'N/A')
            message = (
                f"\n"
                f"Request ID: {request_id}\n"
                f"  Status: {status}\n"
                f"  Query: {query}\n"
                f"  Last Updated: {last_updated}\n"
            )
            messages.append(message)
        
        if messages:
            self.qc_manager.log_info("".join(messages), context="RequestManager")
        

    def clear_requests(self, request_ids: Optional[List[str]] = None) -> None:
        """
        Clear queued or in-progress requests by changing their status to 'cancelled'.

        Args:
            request_ids (List[str], optional): List of request IDs to clear.
                                               If None, clears all queued or in-progress requests.
        """
        self.qc_manager.log_debug("Clearing requests", context="RequestManager")
        self.state_manager.load_state()
        self.state_manager.clear_requests(request_ids)
        if request_ids:
            self.qc_manager.log_info(f"Cleared requests with IDs: {', '.join(request_ids)}", context="RequestManager")
        else:
            self.qc_manager.log_info("Cleared all queued and in-progress requests.", context="RequestManager")