import pytest
from unittest.mock import MagicMock, patch
from dynaconf import Dynaconf
from masa_ai.connections.xtwitter_connection import XTwitterConnection

@pytest.fixture
def mock_global_settings():
    """
    Fixture to mock the entire global_settings object with a MagicMock that includes the 'get' method.
    Applies the mock to all relevant modules.
    """
    mock_settings = MagicMock(spec=Dynaconf)
    mock_settings.get.side_effect = lambda key, default=None: {
        'twitter.BASE_URL': 'https://api.twitter.com/2',
        'twitter.BASE_URL_LOCAL': 'https://api.local.twitter.com/2',
        'twitter.HEADERS': {'Authorization': 'Bearer TOKEN'},
    }.get(key, default)
    
    with patch('masa_ai.connections.api_connection.global_settings', mock_settings), \
         patch('masa_ai.connections.xtwitter_connection.global_settings', mock_settings), \
         patch('masa_ai.configs.config.global_settings', mock_settings):
        yield mock_settings

@pytest.fixture
def mock_qc_manager():
    """
    Fixture to create a mock QCManager instance.
    This patches QCManager in both api_connection and xtwitter_connection modules.
    """
    with patch('masa_ai.connections.api_connection.QCManager', autospec=True) as MockQCManagerApi, \
         patch('masa_ai.connections.xtwitter_connection.QCManager', autospec=True) as MockQCManagerXTwitter:
        
        # Mock methods for APIConnection's QCManager
        instance_api = MockQCManagerApi.return_value
        instance_api.log_debug = MagicMock()
        instance_api.log_warning = MagicMock()
        instance_api.handle_error_with_retry = MagicMock()
        
        # Mock methods for XTwitterConnection's QCManager
        instance_xtwitter = MockQCManagerXTwitter.return_value
        instance_xtwitter.log_debug = MagicMock()
        instance_xtwitter.log_warning = MagicMock()
        instance_xtwitter.handle_error_with_retry = MagicMock()
        
        yield instance_api, instance_xtwitter

@pytest.fixture
def retry_settings():
    """
    Fixture to provide retry settings for RetryPolicy.
    """
    return {
        "twitter": {
            "MAX_RETRIES": 3,
            "BASE_WAIT_TIME": 1,
            "BACKOFF_FACTOR": 2,
            "MAX_WAIT_TIME": 10,
            "INITIAL_WAIT_TIMES": {
                "429": 2,
                "417": 3,
                "504": 4
            },
            "SUCCESS_WAIT_TIME": 1,
            "RETRYABLE_EXCEPTIONS": [
                "RateLimitException",
                "APIException",
                "NoWorkersAvailableException",
                "GatewayTimeoutException",
                "NetworkException"
            ]
        }
    }

@pytest.fixture
def xtwitter_connection(mock_qc_manager, mock_global_settings):
    """
    Fixture to create an instance of XTwitterConnection with mocked QCManager and global_settings.
    """
    return XTwitterConnection() 