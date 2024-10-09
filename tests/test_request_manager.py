# tests/orchestration/test_request_manager.py
"""
Tests for the RequestManager class in the MASA project.

This module contains unit tests for the RequestManager class,
specifically testing the functionality of listing and clearing requests.

Run these tests with pytest.
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
from masa_ai.orchestration.request_manager import RequestManager
from masa_ai.orchestration.state_manager import StateManager
from masa_ai.tools.qc.qc_manager import QCManager
from masa_ai.configs.config import initialize_config

@pytest.fixture
def temp_request_manager():
    """
    Fixture to create a RequestManager instance with temporary state and queue files.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        state_file = temp_dir_path / "request_manager_state.json"
        queue_file = temp_dir_path / "request_queue.json"

        # Initialize config and override ORCHESTRATION_DIR
        initialize_config()
        original_orchestration_dir = os.environ.get('ORCHESTRATION_DIR')
        os.environ['ORCHESTRATION_DIR'] = temp_dir

        try:
            # Create RequestManager with temp files
            request_manager = RequestManager()
            request_manager.state_file = state_file
            request_manager.queue_file = queue_file
            request_manager.state_manager = StateManager(state_file)
            request_manager.state_manager.load_state()
            yield request_manager
        finally:
            # Restore original ORCHESTRATION_DIR
            if original_orchestration_dir:
                os.environ['ORCHESTRATION_DIR'] = original_orchestration_dir
            else:
                del os.environ['ORCHESTRATION_DIR']

def test_request_manager_list_requests_empty(temp_request_manager):
    """
    Test listing requests when there are no requests in the state.
    """
    requests = temp_request_manager.list_requests()
    assert requests == {}

def test_request_manager_list_requests_with_data(temp_request_manager):
    """
    Test listing requests when there are requests with various statuses.
    """
    # Set up state with different request statuses
    temp_request_manager.state_manager._state = {
        'requests': {
            'req1': {'status': 'queued', 'last_updated': '2023-10-01T10:00:00'},
            'req2': {'status': 'in_progress', 'last_updated': '2023-10-01T10:05:00'},
            'req3': {'status': 'completed', 'last_updated': '2023-10-01T10:10:00'},
        },
        'last_updated': '2023-10-01T10:15:00'
    }
    temp_request_manager.state_manager._save_state()
    requests = temp_request_manager.list_requests()
    assert len(requests) == 2  # Should list queued and in-progress by default
    assert 'req1' in requests
    assert 'req2' in requests
    assert 'req3' not in requests

def test_request_manager_clear_all_requests(temp_request_manager):
    """
    Test clearing all queued and in-progress requests.
    """
    # Set up state with requests
    temp_request_manager.state_manager._state = {
        'requests': {
            'req1': {'status': 'queued', 'last_updated': '2023-10-01T10:00:00'},
            'req2': {'status': 'in_progress', 'last_updated': '2023-10-01T10:05:00'},
            'req3': {'status': 'completed', 'last_updated': '2023-10-01T10:10:00'},
            'req4': {'status': 'failed', 'last_updated': '2023-10-01T10:15:00'},
        },
        'last_updated': '2023-10-01T10:20:00'
    }
    temp_request_manager.state_manager._save_state()

    # Clear all queued and in-progress requests
    temp_request_manager.clear_requests()

    # Verify statuses
    updated_state = temp_request_manager.state_manager._state
    assert updated_state['requests']['req1']['status'] == 'cancelled'
    assert updated_state['requests']['req2']['status'] == 'cancelled'
    assert updated_state['requests']['req3']['status'] == 'completed'
    assert updated_state['requests']['req4']['status'] == 'failed'

def test_request_manager_clear_specific_requests(temp_request_manager):
    """
    Test clearing specific requests by IDs.
    """
    # Set up state with requests
    temp_request_manager.state_manager._state = {
        'requests': {
            'req1': {'status': 'queued', 'last_updated': '2023-10-01T10:00:00'},
            'req2': {'status': 'in_progress', 'last_updated': '2023-10-01T10:05:00'},
            'req3': {'status': 'queued', 'last_updated': '2023-10-01T10:10:00'},
        },
        'last_updated': '2023-10-01T10:15:00'
    }
    temp_request_manager.state_manager._save_state()

    # Clear specific requests
    temp_request_manager.clear_requests(request_ids=['req1', 'req3'])

    # Verify statuses
    updated_state = temp_request_manager.state_manager._state
    assert updated_state['requests']['req1']['status'] == 'cancelled'
    assert updated_state['requests']['req2']['status'] == 'in_progress'
    assert updated_state['requests']['req3']['status'] == 'cancelled'

def test_request_manager_process_requests_skips_cancelled(temp_request_manager):
    """
    Test that the RequestManager skips processing cancelled requests.
    """
    # Mock the _process_single_request method to track calls
    temp_request_manager._process_single_request = lambda request_id, request: request_id

    # Set up state with requests
    temp_request_manager.state_manager._state = {
        'requests': {
            'req1': {'status': 'cancelled', 'last_updated': '2023-10-01T10:00:00'},
            'req2': {'status': 'queued', 'last_updated': '2023-10-01T10:05:00'},
        },
        'last_updated': '2023-10-01T10:10:00'
    }
    temp_request_manager.state_manager._save_state()

    # Add requests to queue
    temp_request_manager.queue = temp_request_manager.queue or []
    temp_request_manager.queue.add('req1', {})
    temp_request_manager.queue.add('req2', {})

    # Process queue
    processed_ids = []
    def mock_process_single_request(request_id, request):
        processed_ids.append(request_id)
        temp_request_manager.state_manager.update_request_state(request_id, 'completed')
    temp_request_manager._process_single_request = mock_process_single_request
    temp_request_manager._process_queue()

    # Verify that 'req1' was skipped and 'req2' was processed
    assert 'req1' not in processed_ids
    assert 'req2' in processed_ids

def test_request_manager_list_requests_all_statuses(temp_request_manager):
    """
    Test listing requests with all statuses.
    """
    # Set up state with requests
    temp_request_manager.state_manager._state = {
        'requests': {
            'req1': {'status': 'queued'},
            'req2': {'status': 'in_progress'},
            'req3': {'status': 'completed'},
            'req4': {'status': 'failed'},
            'req5': {'status': 'cancelled'},
        },
        'last_updated': '2023-10-01T10:15:00'
    }
    temp_request_manager.state_manager._save_state()

    # List all requests
    requests = temp_request_manager.list_requests(statuses=None)
    assert len(requests) == 5

    # List requests by specific status
    for status in ['queued', 'in_progress', 'completed', 'failed', 'cancelled']:
        filtered_requests = temp_request_manager.list_requests(statuses=[status])
        assert all(req['status'] == status for req in filtered_requests.values())

def test_request_manager_clear_requests_invalid_ids(temp_request_manager, caplog):
    """
    Test clearing requests with invalid request IDs.
    """
    # Set up state with requests
    temp_request_manager.state_manager._state = {
        'requests': {
            'req1': {'status': 'queued'},
            'req2': {'status': 'in_progress'},
        },
        'last_updated': '2023-10-01T10:15:00'
    }
    temp_request_manager.state_manager._save_state()

    # Clear requests with invalid IDs
    temp_request_manager.clear_requests(request_ids=['req3', 'req4'])

    # Verify that warnings are logged
    warning_messages = [record.getMessage() for record in caplog.records if record.levelname == 'WARNING']
    assert "Request ID req3 not found" in warning_messages[0]
    assert "Request ID req4 not found" in warning_messages[1]
