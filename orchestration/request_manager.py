import os
import hashlib
import json
from datetime import datetime
from .request_router import RequestRouter
from .queue import Queue
from .state_manager import StateManager
from masa_tools.qc.logging import Logger

class RequestManager:
    def __init__(self, config, queue_file=None, state_file=None):
        self.config = config
        self.logger = Logger(__name__)

        orchestration_dir = os.path.dirname(os.path.abspath(__file__))
        self.queue_file = queue_file or os.path.join(orchestration_dir, 'request_queue.json')
        self.state_file = state_file or os.path.join(orchestration_dir, 'state_manager.json')

        self.queue = Queue(self.queue_file)
        self.state_manager = StateManager(self.state_file)
        self.request_router = RequestRouter(self.logger, self.config, self.state_manager)

    def _generate_request_id(self, request):
        request_copy = request.copy()
        request_copy.pop('id', None)
        request_json = json.dumps(request_copy, sort_keys=True).encode('utf-8')
        return hashlib.sha256(request_json).hexdigest()

    def add_request(self, request):
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

    def process_requests(self):
        in_progress_requests = self._get_in_progress_requests()
        for request in in_progress_requests:
            self._process_single_request(request)

        while True:
            request = self.queue.get()
            if not request:
                break
            self._process_single_request(request)

    def _get_in_progress_requests(self):
        all_requests = self.state_manager.get_all_requests_state()
        return [
            request['original_request']
            for request in all_requests.values()
            if request.get('status') == 'in_progress' and 'original_request' in request
        ]

    def _process_single_request(self, request):
        request_id = request['id']
        self.logger.log_info(f"Processing request {request_id}")
        try:
            self.state_manager.update_request_state(request_id, 'in_progress', original_request=request)
            self.request_router.route_request(request)
            self.queue.complete(request_id)
            self.state_manager.update_request_state(request_id, 'completed', original_request=request)
            self.logger.log_info(f"Completed request {request_id}")
        except Exception as e:
            self.logger.log_error(f"Error processing request {request_id}: {str(e)}")
            self.queue.fail(request_id, str(e))
            self.state_manager.update_request_state(request_id, 'failed', progress={'error': str(e)}, original_request=request)

    def get_request_status(self, request_id):
        return self.state_manager.get_request_state(request_id)

    def get_all_requests_status(self):
        return self.state_manager.get_all_requests_state()

    def resume_incomplete_requests(self):
        self.queue.resume_incomplete_requests()