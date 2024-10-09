# tests/orchestration/test_state_manager.py
"""
Tests for the StateManager class in the MASA project.

This module contains unit tests for the StateManager class,
specifically testing the methods related to request state management.

Run these tests with pytest.
"""

import pytest
import tempfile
import json
from pathlib import Path
from masa_ai.orchestration.state_manager import StateManager
from masa_ai.tools.qc.qc_manager import QCManager

@pytest.fixture
def temp_state_manager():
    """
    Fixture to create a StateManager instance with a temporary state file.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        state_file = Path(temp_dir) / "request_manager_state.json"
        state_manager = StateManager(state_file)
        state_manager.load_state()
        yield state_manager

def test_state_manager_get_requests_by_status(temp_state_manager):
    """
    Test getting requests by status.
    """
    temp_state_manager._state = {
        'requests': {
            'req1': {'status': 'queued'},
            'req2': {'status': 'in_progress'},
            'req3': {'status': 'completed'},
            'req4': {'status': 'failed'},
        },
        'last_updated': '2023-10-01T10:20:00'
    }

    queued_requests = temp_state_manager.get_requests_by_status(['queued'])
    assert len(queued_requests) == 1
    assert 'req1' in queued_requests

    all_requests = temp_state_manager.get_requests_by_status()
    assert len(all_requests) == 4

def test_state_manager_clear_requests(temp_state_manager):
    """
    Test clearing requests by status and IDs.
    """
    temp_state_manager._state = {
        'requests': {
            'req1': {'status': 'queued'},
            'req2': {'status': 'in_progress'},
            'req3': {'status': 'completed'},
        },
        'last_updated': '2023-10-01T10:20:00'
    }

    # Clear all queued and in-progress requests
    temp_state_manager.clear_requests()
    assert temp_state_manager._state['requests']['req1']['status'] == 'cancelled'
    assert temp_state_manager._state['requests']['req2']['status'] == 'cancelled'
    assert temp_state_manager._state['requests']['req3']['status'] == 'completed'

    # Reset state
    temp_state_manager._state['requests']['req1']['status'] = 'queued'
    temp_state_manager._state['requests']['req2']['status'] = 'in_progress'

    # Clear specific requests
    temp_state_manager.clear_requests(request_ids=['req1'])
    assert temp_state_manager._state['requests']['req1']['status'] == 'cancelled'
    assert temp_state_manager._state['requests']['req2']['status'] == 'in_progress'

def test_state_manager_thread_safety(temp_state_manager):
    """
    Test that StateManager methods are thread-safe.
    """
    import threading

    def update_state():
        for _ in range(100):
            temp_state_manager.update_request_state('req1', 'queued')
            temp_state_manager.update_request_state('req1', 'completed')

    threads = [threading.Thread(target=update_state) for _ in range(10)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    # Verify that the state is consistent
    final_status = temp_state_manager.get_request_state('req1')['status']
    assert final_status in ['queued', 'completed']
