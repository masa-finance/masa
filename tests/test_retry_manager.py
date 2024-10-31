import pytest
from unittest.mock import MagicMock, patch
from masa_ai.tools.qc.retry_manager import RetryPolicy
from masa_ai.tools.qc.exceptions import (
    RateLimitException,
    APIException,
    NoWorkersAvailableException,
    GatewayTimeoutException,
    NetworkException,
)


@pytest.fixture
def mock_qc_manager():
    """
    Fixture to create a mock QCManager instance.

    Returns:
        MagicMock: A mocked QCManager.
    """
    return MagicMock()


@pytest.fixture
def retry_settings():
    """
    Fixture to provide retry settings for RetryPolicy.

    Returns:
        dict: A dictionary containing retry configurations.
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


def test_execute_with_retry_success(mock_qc_manager, retry_settings):
    """
    Test that execute_with_retry successfully executes the function without retries when no exception is raised.

    Args:
        mock_qc_manager (MagicMock): Mocked QCManager.
        retry_settings (dict): Retry configuration settings.
    """
    policy = RetryPolicy(settings=retry_settings, qc_manager=mock_qc_manager)

    mock_func = MagicMock(return_value="success")

    result = policy.execute_with_retry(mock_func, "twitter")

    assert result == "success"
    mock_func.assert_called_once()
    mock_qc_manager.log_debug.assert_not_called()  # Updated assertion


def test_execute_with_retry_retryable_exception(mock_qc_manager, retry_settings):
    """
    Test that execute_with_retry retries the correct number of times when a retryable exception is raised.

    Args:
        mock_qc_manager (MagicMock): Mocked QCManager.
        retry_settings (dict): Retry configuration settings.
    """
    policy = RetryPolicy(settings=retry_settings, qc_manager=mock_qc_manager)

    mock_func = MagicMock(side_effect=RateLimitException("Rate limit exceeded"))

    with pytest.raises(RateLimitException):
        policy.execute_with_retry(mock_func, "twitter")

    assert mock_func.call_count == retry_settings["twitter"]["MAX_RETRIES"]
    assert mock_qc_manager.log_warning.call_count == retry_settings["twitter"]["MAX_RETRIES"] - 1


def test_execute_with_retry_non_retryable_exception(mock_qc_manager, retry_settings):
    """
    Test that execute_with_retry does not retry when a non-retryable exception is raised.

    Args:
        mock_qc_manager (MagicMock): Mocked QCManager.
        retry_settings (dict): Retry configuration settings.
    """
    # Initialize RetryPolicy with the full settings dictionary
    policy = RetryPolicy(settings=retry_settings, qc_manager=mock_qc_manager)

    mock_func = MagicMock(side_effect=ValueError("Non-retryable error"))

    with pytest.raises(ValueError):
        policy.execute_with_retry(mock_func, "twitter")

    mock_func.assert_called_once()
    mock_qc_manager.log_warning.assert_not_called()


def test_wait_time_rate_limit_exception(mock_qc_manager, retry_settings):
    """
    Test the calculation of wait_time for RateLimitException.

    Args:
        mock_qc_manager (MagicMock): Mocked QCManager.
        retry_settings (dict): Retry configuration settings.
    """
    policy = RetryPolicy(settings=retry_settings, qc_manager=mock_qc_manager)
    config = policy.get_configuration("twitter")

    wait = policy.wait_time(config, attempt=1, exception=RateLimitException("Rate limit"))

    assert wait == 2
    mock_qc_manager.log_debug.assert_called_with(
        "Waiting for 2 seconds before retry", context="RetryPolicy"
    )


def test_wait_time_api_exception_with_status_code(mock_qc_manager, retry_settings):
    """
    Test the calculation of wait_time for APIException with a specific status code.

    Args:
        mock_qc_manager (MagicMock): Mocked QCManager.
        retry_settings (dict): Retry configuration settings.
    """
    policy = RetryPolicy(settings=retry_settings, qc_manager=mock_qc_manager)
    config = policy.get_configuration("twitter")

    api_exception = APIException("API error")
    api_exception.status_code = 504 

    wait = policy.wait_time(config, attempt=1, exception=api_exception)

    assert wait == 4
    mock_qc_manager.log_debug.assert_called_with(
        "Waiting for 4 seconds before retry", context="RetryPolicy"
    )


def test_should_retry_true_for_retryable_exception(mock_qc_manager, retry_settings):
    """
    Test that should_retry returns True for a retryable exception within retry limits.

    Args:
        mock_qc_manager (MagicMock): Mocked QCManager.
        retry_settings (dict): Retry configuration settings.
    """
    policy = RetryPolicy(settings=retry_settings, qc_manager=mock_qc_manager)
    config = policy.get_configuration("twitter")

    should = policy.should_retry(config, RateLimitException("Rate limit"), attempt=1)

    assert should is True


def test_should_retry_false_after_max_retries(mock_qc_manager, retry_settings):
    """
    Test that should_retry returns False when maximum retries have been reached.

    Args:
        mock_qc_manager (MagicMock): Mocked QCManager.
        retry_settings (dict): Retry configuration settings.
    """
    policy = RetryPolicy(settings=retry_settings, qc_manager=mock_qc_manager)
    config = policy.get_configuration("twitter")

    should = policy.should_retry(config, RateLimitException("Rate limit"), attempt=3)

    assert should is False


def test_wait_with_progress(mock_qc_manager, retry_settings):
    """
    Test the wait_with_progress method to ensure it waits for the specified time.

    Args:
        mock_qc_manager (MagicMock): Mocked QCManager.
        retry_settings (dict): Retry configuration settings.
    """
    policy = RetryPolicy(settings=retry_settings, qc_manager=mock_qc_manager)

    with patch("time.sleep", return_value=None) as mock_sleep, \
         patch("masa_ai.tools.qc.retry_manager.tqdm") as mock_tqdm:
        mock_pbar = MagicMock()
        mock_pbar.n = 0.0  # Initialize 'n' as a float

        # Define a side effect function to update 'n' when 'update' is called
        def update_side_effect(amount):
            mock_pbar.n += amount

        mock_pbar.update.side_effect = update_side_effect
        mock_tqdm.return_value.__enter__.return_value = mock_pbar

        policy.wait_with_progress(2)

        # Assert that sleep was called multiple times to simulate waiting
        assert mock_sleep.call_count > 0
        # Assert that pbar.update was called to reflect progress updates
        mock_pbar.update.assert_called()
