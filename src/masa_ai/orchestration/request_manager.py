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
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from masa_ai.tools.database.models.entities.request import Request
from masa_ai.tools.database.models.entities.tweet import Tweet
from masa_ai.orchestration.request_router import RequestRouter
from masa_ai.orchestration.queue import Queue
from masa_ai.tools.qc.qc_manager import QCManager
from masa_ai.configs.config import global_settings
from masa_ai.tools.database.abstract_database_handler import AbstractDatabaseHandler
from masa_ai.tools.database.duckdb_handler import DuckDBHandler

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
        
        # Initialize database handler
        db_path = self.config.get('database.PATH', 'masa.db')
        self.db_handler: AbstractDatabaseHandler = DuckDBHandler(db_path, self.qc_manager)
        
        self.request_router = RequestRouter(
            self.qc_manager, 
            self.db_handler
        )
        self.queue = None

    def process_requests(self, requests: Optional[List[Dict[str, Any]]] = None):
        """
        Process requests from input or existing queue.

        This method is the main entry point for request processing. It loads
        requests from a file if provided, otherwise processes requests from
        the existing queue.

        Args:
            requests (List[Dict[str, Any]], optional): List of requests to process. If None, process the existing queue.
        """
        
        # Initialize queue if not already done
        if self.queue is None:
            self.queue = Queue(self.db_handler)
        
        if requests:
            self._update_state_with_requests(requests)
        else:
            # Only resync if we're not adding new requests
            self.queue._sync_with_database()

        # Process the requests
        self._process_queue()

    def _update_state_with_requests(self, requests: List[Dict[str, Any]]):
        """
        Update the state manager with new requests.

        Args:
            requests (List[Dict[str, Any]]): List of requests.
        """
        self.qc_manager.log_debug("Adding new requests to database and queue", context="RequestManager")
        for request_data in requests:
            request_id = self._generate_request_id(request_data)
            request_data['request_id'] = request_id
            
            # Check if request exists
            existing_request = self.db_handler.get_request_by_id(request_id)
            if not existing_request:
                # Create new Request instance
                request = Request(
                    request_id=request_id,
                    status='queued',
                    created_at=datetime.utcnow(),
                    last_updated=datetime.utcnow(),
                    scraper=request_data.get('scraper', ''),
                    endpoint=request_data.get('endpoint', ''),
                    priority=request_data.get('priority', 1),
                    params=request_data.get('params', {}),
                    progress={},
                    result={},
                    error=None
                )
                # Add to database
                self.db_handler.add_request(request)
                
                # Add to queue directly
                self.queue.add({
                    'request_id': request_id,
                    'priority': request_data.get('priority', 1),
                    **request_data
                })
                
                self.qc_manager.log_info(f"Added new request {request_id} to database and queue")

    def _process_queue(self):
        """
        Process requests from the queue.
        """
        requests = self.db_handler.get_all_requests()
        queued_requests = [r for r in requests if r['status'] == 'queued']
        
        total_requests = len(queued_requests)
        self.qc_manager.log_info(f"Starting to process {total_requests} requests")

        for request in queued_requests:
            try:
                self._process_single_request(request['request_id'], request)
            except Exception as e:
                self.qc_manager.log_error(f"Error processing request: {str(e)}", context="RequestManager")

    def _process_single_request(self, request_id: str, request: Dict[str, Any]):
        """
        Process a single request.

        Args:
            request_id (str): The ID of the request.
            request (dict): The request to process.

        Raises:
            Exception: If an error occurs during request processing.
        """
        try:
            # Update request status to in_progress
            self.db_handler.update_request_status(request_id, 'in_progress', {})
            
            result = self.request_router.route_request(request_id, request)
            
            # Update request with completed status and result
            self.db_handler.update_request_status(
                request_id, 
                'completed',
                {'result': result}
            )
            
            self.qc_manager.log_info(f"Request completed: {request_id}")
        except Exception as e:
            self.qc_manager.log_error(f"Error in request {request_id}: {str(e)}")
            self.db_handler.update_request_status(
                request_id,
                'failed',
                {'error': str(e)}
            )
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

    def get_request_status(self, request_id: str) -> Dict[str, Any]:
        """Get the status of a request."""
        return self.db_handler.get_request_by_id(request_id)

    def get_all_requests_status(self) -> List[Dict[str, Any]]:
        """Get the status of all requests."""
        return self.db_handler.get_all_requests()

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

    def cancel_request(self, request_id: str):
        """Cancel a specific request."""
        try:
            self.db_handler.update_request_status(
                request_id,
                'cancelled',
                {'cancelled_at': datetime.utcnow().isoformat()}
            )
            self.qc_manager.log_info(f"Cancelled request {request_id}", context="RequestManager")
        except Exception as e:
            self.qc_manager.log_warning(f"Failed to cancel request {request_id}: {str(e)}", context="RequestManager")

    def list_requests(self, statuses: Optional[List[str]] = None):
        """List requests with their details."""
        requests = self.db_handler.get_all_requests()
        
        if statuses:
            requests = [r for r in requests if r['status'] in statuses]
        
        if not requests:
            self.qc_manager.log_info("No requests found.", context="RequestManager")
            return

        for request in requests:
            message = (
                f"\nRequest ID: {request['request_id']}\n"
                f"  Status: {request['status']}\n"
                f"  Query: {request['params'].get('query', 'N/A')}\n"
                f"  Last Updated: {request['last_updated']}\n"
            )
            self.qc_manager.log_info(message, context="RequestManager")

    def clear_requests(self, request_ids: Optional[List[str]] = None):
        """Clear requests by marking them as cancelled."""
        if request_ids:
            for request_id in request_ids:
                self.cancel_request(request_id)
        else:
            requests = self.db_handler.get_all_requests()
            for request in requests:
                if request['status'] in ['queued', 'in_progress']:
                    self.cancel_request(request['request_id'])