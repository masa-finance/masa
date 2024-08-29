import os
import hashlib
import json
from datetime import datetime
from .request_router import RequestRouter
from .queue import Queue
from .state_manager import StateManager
from masa_tools.qc.qc_manager import QCManager
from configs.config import global_settings
import traceback

class RequestManager:
    def __init__(self):
        self.qc_manager = QCManager()
        self.config = global_settings
        self.state_file = self.config.get('request_manager.STATE_FILE')
        self.state_manager = StateManager(self.state_file)
        self.request_router = RequestRouter(self.qc_manager, self.state_manager)
        self.queue_file = self.config.get('request_manager.QUEUE_FILE')
        self.queue = Queue(self.queue_file, self.state_manager)

    def process_requests(self, request_list_file=None):
        if request_list_file:
            self.add_requests_from_file(request_list_file)

        self.queue.resume_incomplete_requests()
        
        while True:
            request = self.queue.get()
            if request is None:
                self.qc_manager.log_debug("Queue is empty. Exiting process_requests.", context="RequestManager")
                break

            self.qc_manager.log_debug(f"Retrieved request from queue: {request}", context="RequestManager")

            if 'id' not in request:
                self.qc_manager.log_warning(f"Request does not have an 'id' key: {request}", context="RequestManager")
                request_id = self._generate_request_id(request)
                request['id'] = request_id
                self.qc_manager.log_info(f"Generated new id for request: {request_id}", context="RequestManager")
            
            if 'status' not in request:
                request['status'] = 'queued'
                self.state_manager.update_request_state(request['id'], 'queued', original_request=request)
            
            self.qc_manager.log_info(f"Processing request: {request['id']} with status {request['status']}", context="RequestManager")
            
            try:
                self._process_single_request(request)
            except Exception as e:
                self.qc_manager.log_error(f"Error processing request {request['id']}: {str(e)}", error_info=e, context="RequestManager")

    def add_requests_from_file(self, request_list_file):
        self.qc_manager.log_debug(f"Loading requests from file: {request_list_file}", context="RequestManager")
        with open(request_list_file, 'r') as file:
            requests = json.load(file)
            if isinstance(requests, list):
                for request in requests:
                    generated_id = self._generate_request_id(request)
                    if generated_id in self.queue.request_data:
                        self.qc_manager.log_debug(f"Duplicate request found: {generated_id}.  Skipping.", context="RequestManager")
                        continue
                    request['id'] = generated_id
                    if 'status' not in request:
                        request['status'] = 'queued'
                    self.queue.add(request)
                    self.state_manager.update_request_state(request['id'], request['status'], original_request=request)
                self.qc_manager.log_info(f"Loaded {len(requests)} requests from file", context="RequestManager")
            else:
                self.qc_manager.log_error("Invalid JSON structure in request_list.json. Expected a list of requests.", context="RequestManager")

    def _generate_request_id(self, request):
        request_copy = request.copy()
        request_copy.pop('id', None) 
        request_json = json.dumps(request_copy, sort_keys=True).encode('utf-8')
        return hashlib.sha256(request_json).hexdigest()

    def prompt_user_for_queue_action(self, request_list_file):
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
        request_id = request['id']
        self.qc_manager.log_debug(f"Adding request {request_id} to system", context="RequestManager")
        
        self.queue.add(request)
        self.state_manager.update_request_state(request_id, 'queued', original_request=request)
        self.qc_manager.log_debug(f"Request {request_id} added to queue and state updated", context="RequestManager")

    def get_request_status(self, request_id):
        return self.state_manager.get_request_state(request_id)

    def get_all_requests_status(self):
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
        self.queue.resume_incomplete_requests()

    def cancel_request_queue(self, request_list_file):
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
        request_state = self.state_manager.get_request_state(request_id)
        if request_state:
            self.state_manager.update_request_state(request_id, 'cancelled')
            self.qc_manager.log_info(f"Cancelled request {request_id}", context="RequestManager")
        else:
            self.qc_manager.log_warning(f"Request {request_id} not found in the state manager", context="RequestManager")

    def _process_single_request(self, request):
        """
        Process a single request.

        :param request: The request dictionary to process.
        """
        request_id = request['id']
        self.qc_manager.log_debug(f"Processing request {request_id}", context="RequestManager")
        try:
            self.state_manager.update_request_state(request_id, 'in_progress', original_request=request)
            self.qc_manager.log_debug(f"Updated state for request {request_id} to in_progress", context="RequestManager")
            
            self.qc_manager.log_debug(f"Routing request {request_id}", context="RequestManager")
            self.request_router.route_request(request)
            
            self.queue.complete(request_id)
            self.state_manager.update_request_state(request_id, 'completed', original_request=request)
            self.qc_manager.log_debug(f"Request {request_id} completed successfully", context="RequestManager")
        except Exception as e:
            self.qc_manager.log_error(f"Error processing request {request_id}: {str(e)}", error_info=e, context="RequestManager")
            self.qc_manager.log_error(f"Traceback: {traceback.format_exc()}", context="RequestManager")
            
            self.queue.fail(request_id, str(e))
            self.state_manager.update_request_state(request_id, 'failed', progress={'error': str(e)}, original_request=request)
            
            # Note: Retry logic has been removed as it's not handled here in the current structure