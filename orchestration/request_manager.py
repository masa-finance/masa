"""
Request Manager module for the MASA project.

This module provides the RequestManager class, which is responsible for
orchestrating the overall request processing workflow in the MASA system.
"""

import os
import hashlib
import json
from datetime import datetime
from .request_router import RequestRouter
from .queue import Queue
from .state_manager import StateManager
from tools.qc.qc_manager import QCManager
from configs.config import global_settings
import traceback

class RequestManager:
    """
    RequestManager class for orchestrating request processing.

    This class manages the lifecycle of requests, including queueing,
    routing, processing, and state management. It integrates various
    components of the MASA system to ensure efficient and reliable
    request handling.

    Attributes:
        qc_manager (tools.qc.qc_manager.QCManager): Quality control manager for logging and error handling.
        config (dict): Configuration settings for the request manager.
        state_manager (orchestration.state_manager.StateManager): Manager for handling request states.
        request_router (orchestration.request_router.RequestRouter): Router for directing requests to appropriate handlers.
        queue (orchestration.queue.Queue): Priority queue for managing requests.
    """
    def __init__(self):
        """
        Initialize the RequestManager.
        """
        self.qc_manager = QCManager()
        self.config = global_settings
        self.state_file = self.config.get('request_manager.STATE_FILE')
        self.queue_file = self.config.get('request_manager.QUEUE_FILE')
        self.state_manager = StateManager(self.state_file)
        self.request_router = RequestRouter(self.qc_manager, self.state_manager)
        self.queue = Queue(self.state_manager, self.queue_file)

    def process_requests(self, request_list_file=None):
        """
        Process requests from a file or the existing queue.

        This method is the main entry point for request processing. It loads
        requests from a file if provided, otherwise processes requests from
        the existing queue.

        Args:
            request_list_file (str, optional): Path to a JSON file containing requests to process.

        Returns:
            None
        """
        if request_list_file:
            self.add_requests_from_file(request_list_file)
            self.qc_manager.log_info(f"Loaded requests from file: {request_list_file}")
    
        total_requests = len(self.queue.memory_queue.queue)
        self.qc_manager.log_info(f"Starting to process {total_requests} requests")

        processed_requests = 0
        while True:
            request = self.queue.get()
            if request is None:
                break

            processed_requests += 1
            self.qc_manager.log_info(f"Processing request {processed_requests} of {total_requests}")

            try:
                self._process_single_request(request)
            except Exception as e:
                self.qc_manager.log_error(f"Error processing request: {str(e)}")

        self.qc_manager.log_info(f"Completed processing all {total_requests} requests")

    def _process_single_request(self, request):
        """
        Process a single request.

        Args:
            request (dict): The request to process.

        Raises:
            Exception: If an error occurs during request processing.
        """
        request_id = request['id']
        current_state = self.state_manager.get_request_state(request_id)

        self.qc_manager.log_debug(f"Processing request {request_id}, Current status: {current_state['status']}", context="RequestManager")

        if current_state['status'] != 'in_progress':
            self.state_manager.update_request_state(request_id, 'in_progress', request_details=request)

        try:
            result = self.request_router.route_request(request)
            self.state_manager.update_request_state(request_id, 'completed', result=result)
            self.qc_manager.log_info(f"Request completed: {request_id}")
        except Exception as e:
            self.qc_manager.log_error(f"Error in request {request_id}: {str(e)}")
            self.state_manager.update_request_state(request_id, 'failed', error=str(e))
            raise

    def add_requests_from_file(self, request_list_file):
        """
        Add requests from a JSON file to the queue.

        Args:
            request_list_file (str): Path to the JSON file containing requests.
        """
        self.qc_manager.log_debug(f"Loading requests from file: {request_list_file}", context="RequestManager")
        with open(request_list_file, 'r') as file:
            requests = json.load(file)
            if isinstance(requests, list):
                for request in requests:
                    generated_id = self._generate_request_id(request)
                    request['id'] = generated_id
                    existing_state = self.state_manager.get_request_state(generated_id)
                    if not existing_state or existing_state.get('status') in ['failed', 'cancelled']:
                        request['status'] = 'queued'
                        self.queue.add(request)
                        self.state_manager.update_request_state(request['id'], 'queued', request_details=request)
                    else:
                        self.qc_manager.log_debug(f"Skipping existing request: {generated_id}", context="RequestManager")
                self.qc_manager.log_info(f"Added {len(requests)} new requests from file")
            else:
                self.qc_manager.log_error("Invalid JSON structure in request_list.json. Expected a list of requests.", context="RequestManager")

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

    def load_request_list(self, request_list_file):
        """
        Load the request list from a JSON file.

        Args:
            request_list_file (str): Path to the JSON file containing requests.

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
