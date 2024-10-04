# tests/masa/test_masa.py
"""
Tests for the Masa class in the MASA project.

This module contains unit tests for the Masa class,
specifically testing the interaction with the RequestManager
for listing and clearing requests.

Run these tests with pytest.
"""

import pytest
from unittest.mock import MagicMock
from masa_ai.masa import Masa
from masa_ai.orchestration.request_manager import RequestManager
from masa_ai.configs.config import initialize_config

@pytest.fixture
def masa_with_mocked_request_manager():
    """
    Fixture to create a Masa instance with a mocked RequestManager.
    """
    initialize_config()
    masa = Masa()
    masa.request_manager = MagicMock(spec=RequestManager)
    return masa

def test_masa_list_requests_calls_request_manager(masa_with_mocked_request_manager):
    """
    Test that Masa.list_requests calls the RequestManager.list_requests method.
    """
    masa_with_mocked_request_manager.list_requests(statuses=['queued', 'in_progress'])
    masa_with_mocked_request_manager.request_manager.list_requests.assert_called_once_with(['queued', 'in_progress'])

def test_masa_clear_requests_calls_request_manager(masa_with_mocked_request_manager):
    """
    Test that Masa.clear_requests calls the RequestManager.clear_requests method.
    """
    masa_with_mocked_request_manager.clear_requests(request_ids=['req1', 'req2'])
    masa_with_mocked_request_manager.request_manager.clear_requests.assert_called_once_with(['req1', 'req2'])

def test_masa_clear_all_requests_calls_request_manager(masa_with_mocked_request_manager):
    """
    Test that Masa.clear_requests with no IDs calls RequestManager.clear_requests with None.
    """
    masa_with_mocked_request_manager.clear_requests()
    masa_with_mocked_request_manager.request_manager.clear_requests.assert_called_once_with(None)
