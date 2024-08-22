import json
import os
from collections import deque
from datetime import datetime
import hashlib
from masa_tools.qc.logging import Logger
import logging

class Queue:
    def __init__(self, file_path):
        self.file_path = file_path
        self.memory_queue = deque()
        self.request_data = {}
        self.logger = Logger()  # Initialize the logger
        self._load_queue()

    def _load_queue(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                self.request_data = data['requests']
                self.memory_queue = deque(data['queue'])
        else:
            self.request_data = {}
            self.memory_queue = deque()

    def _save_queue(self):
        with open(self.file_path, 'w') as f:
            json.dump({
                'queue': list(self.memory_queue),
                'requests': self.request_data
            }, f, indent=2)

    def add(self, request):
        request_id = request['id']
        if request_id in self.request_data and self.request_data[request_id]['status'] in ['completed', 'in_progress']:
            return

        self.request_data[request_id] = {
            'request': request,
            'status': 'queued',
            'created_at': datetime.now().isoformat()
        }
        if request_id not in self.memory_queue:
            self.memory_queue.append(request_id)
        self._save_queue()

    def get(self):
        if not self.memory_queue:
            return None

        request_id = self.memory_queue.popleft()
        request_info = self.request_data.get(request_id)
        if request_info:
            request_info['status'] = 'in_progress'
            self._save_queue()
            return request_info['request']
        return None

    def complete(self, request_id):
        if request_id in self.request_data:
            self.request_data[request_id]['status'] = 'completed'
            self._save_queue()
        else:
            self.logger.log_warning(f"Request {request_id} not found for completion")

    def fail(self, request_id, error):
        if request_id in self.request_data:
            self.request_data[request_id]['status'] = 'failed'
            self.request_data[request_id]['error'] = str(error)
            self._save_queue()
        else:
            self.logger.log_warning(f"Request {request_id} not found for failure logging")

    def get_status(self, request_id):
        return self.request_data.get(request_id)

    def get_all_statuses(self):
        return self.request_data

    def resume_incomplete_requests(self):
        for request_id, request_info in self.request_data.items():
            if request_info['status'] in ['queued', 'in_progress']:
                if request_id not in self.memory_queue:
                    self.memory_queue.append(request_id)
        self._save_queue()

    # def prompt_user_for_queue_action(self):
    #     if self.memory_queue:
    #         self.logger.log_info("Existing requests in the queue:")
    #         for request_id in self.memory_queue:
    #             self.logger.log_info(f"Request ID: {request_id}, Status: {self.request_data[request_id]['status']}")

    #         user_input = input("Do you want to continue with these requests? (yes/no): ").strip().lower()
    #         if user_input == 'no':
    #             self.clear_queue()
    #             self.logger.log_info("Queue has been cleared. You can add new requests now.")
    #         else:
    #             self.logger.log_info("Continuing with existing requests.")
    #     else:
    #         self.logger.log_info("No existing requests in the queue. You can add new requests.")

    def clear_queue(self):
        self.memory_queue.clear()
        self.request_data = {}
        self._save_queue()