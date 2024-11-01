import pytest
from unittest.mock import patch, MagicMock
from masa_ai.connections.xtwitter_connection import XTwitterConnection
from masa_ai.tools.qc.exceptions import (
    RateLimitException,
    APIException,
    NoWorkersAvailableException,
    AuthenticationException,
    NetworkException,
    GatewayTimeoutException
)
from masa_ai.tools.qc.retry_manager import RetryPolicy

@pytest.mark.integration
class TestIntegrationXTwitterConnection:
    def test_successful_request(self, xtwitter_connection):
        """
        Test that a successful request returns the expected data without retries.
        
        Args:
            xtwitter_connection (XTwitterConnection): The XTwitterConnection instance.
        """
        with patch.object(
            XTwitterConnection, 
            '_make_request', 
            return_value=MagicMock(
                status_code=200, 
                json=lambda: {"data": [{"id": "1", "text": "Test tweet"}]}
            )
        ) as mock_make_request:
            result = xtwitter_connection.get_tweets('endpoint', 'query', 10)
            assert result == {"data": [{"id": "1", "text": "Test tweet"}]}
            mock_make_request.assert_called_once_with(
                'POST', 
                'https://api.twitter.com/2/endpoint', 
                data={'query': 'query', 'count': 10}
            )

    def test_retry_on_rate_limit_exception(self, xtwitter_connection, mock_qc_manager, retry_settings):
        """
        Test that a RateLimitException triggers the retry logic.
        
        Args:
            xtwitter_connection (XTwitterConnection): The XTwitterConnection instance.
            mock_qc_manager (MagicMock): Mocked QCManager.
            retry_settings (dict): Retry configuration settings.
        """
        with patch(
            'masa_ai.tools.qc.retry_manager.time.sleep', 
            return_value=None
        ), patch(
            'masa_ai.tools.qc.retry_manager.tqdm', 
            MagicMock()
        ):
            # Patch RetryPolicy.execute_with_retry to immediately call the function without actual retries
            with patch.object(
                RetryPolicy, 
                'execute_with_retry',
                side_effect=lambda func, config_key, *args, **kwargs: func(*args, **kwargs)
            ) as mock_execute_with_retry:
                # Make _make_request always raise RateLimitException to trigger retries
                with patch.object(
                    XTwitterConnection, 
                    '_make_request', 
                    side_effect=RateLimitException("Rate limit exceeded")
                ) as mock_make_request:
                    with pytest.raises(RateLimitException):
                        xtwitter_connection.get_tweets('endpoint', 'query', 10)
                    
                    assert mock_make_request.call_count == retry_settings["twitter"]["MAX_RETRIES"]

    def test_no_retry_on_authentication_exception(self, xtwitter_connection, mock_qc_manager, retry_settings):
        """
        Test that an AuthenticationException does not trigger retries.
        
        Args:
            xtwitter_connection (XTwitterConnection): The XTwitterConnection instance.
            mock_qc_manager (MagicMock): Mocked QCManager.
            retry_settings (dict): Retry configuration settings.
        """
        with patch(
            'masa_ai.tools.qc.retry_manager.time.sleep', 
            return_value=None
        ), patch(
            'masa_ai.tools.qc.retry_manager.tqdm', 
            MagicMock()
        ):
            # Patch RetryPolicy.execute_with_retry to immediately call the function without actual retries
            with patch.object(
                RetryPolicy, 
                'execute_with_retry',
                side_effect=lambda func, config_key, *args, **kwargs: func(*args, **kwargs)
            ) as mock_execute_with_retry:
                # Make _make_request raise AuthenticationException
                with patch.object(
                    XTwitterConnection, 
                    '_make_request', 
                    side_effect=AuthenticationException("Authentication failed")
                ) as mock_make_request:
                    with pytest.raises(AuthenticationException):
                        xtwitter_connection.get_tweets('endpoint', 'query', 10)
                    
                    assert mock_make_request.call_count == 1
                    # Ensure no retry warnings were logged
                    mock_qc_manager.log_warning.assert_not_called()

    def test_retry_with_mixed_exceptions(self, xtwitter_connection, mock_qc_manager, retry_settings):
        """
        Test retry logic with a mix of retryable and non-retryable exceptions.
        
        Args:
            xtwitter_connection (XTwitterConnection): The XTwitterConnection instance.
            mock_qc_manager (MagicMock): Mocked QCManager.
            retry_settings (dict): Retry configuration settings.
        """
        with patch(
            'masa_ai.tools.qc.retry_manager.time.sleep', 
            return_value=None
        ), patch(
            'masa_ai.tools.qc.retry_manager.tqdm', 
            MagicMock()
        ):
            # Patch RetryPolicy.execute_with_retry to immediately call the function without actual retries
            with patch.object(
                RetryPolicy, 
                'execute_with_retry',
                side_effect=lambda func, config_key, *args, **kwargs: func(*args, **kwargs)
            ) as mock_execute_with_retry:
                # First attempt raises RateLimitException, second raises NetworkException, third succeeds
                mock_make_request = MagicMock(side_effect=[
                    RateLimitException("Rate limit exceeded"),
                    NetworkException("Network error"),
                    MagicMock(status_code=200, json=lambda: {"data": [{"id": "2", "text": "Another test tweet"}]})
                ])
                with patch.object(
                    XTwitterConnection, 
                    '_make_request', 
                    mock_make_request
                ):
                    result = xtwitter_connection.get_tweets('endpoint', 'query', 10)
                    assert result == {"data": [{"id": "2", "text": "Another test tweet"}]}
                    assert mock_make_request.call_count == 3
                    assert mock_qc_manager.log_warning.call_count == 2

    def test_retry_timeout_exception(self, xtwitter_connection, mock_qc_manager, retry_settings):
        """
        Test that a GatewayTimeoutException triggers retry logic.
        
        Args:
            xtwitter_connection (XTwitterConnection): The XTwitterConnection instance.
            mock_qc_manager (MagicMock): Mocked QCManager.
            retry_settings (dict): Retry configuration settings.
        """
        with patch(
            'masa_ai.tools.qc.retry_manager.time.sleep', 
            return_value=None
        ), patch(
            'masa_ai.tools.qc.retry_manager.tqdm', 
            MagicMock()
        ):
            # Patch RetryPolicy.execute_with_retry to immediately call the function without actual retries
            with patch.object(
                RetryPolicy, 
                'execute_with_retry',
                side_effect=lambda func, config_key, *args, **kwargs: func(*args, **kwargs)
            ) as mock_execute_with_retry:
                # Make _make_request always raise GatewayTimeoutException to trigger retries
                with patch.object(
                    XTwitterConnection, 
                    '_make_request', 
                    side_effect=GatewayTimeoutException("Gateway timeout")
                ) as mock_make_request:
                    with pytest.raises(GatewayTimeoutException):
                        xtwitter_connection.get_tweets('endpoint', 'query', 10)
                    
                    assert mock_make_request.call_count == retry_settings["twitter"]["MAX_RETRIES"]
                    mock_qc_manager.log_warning.assert_called()