import pytest
from masa_ai.tools.validator import TweetValidator
from masa_ai.tools.validator.main import main as validate_main
from loguru import logger
import sys

@pytest.fixture(scope="module", autouse=True)
def setup_logging():
    """Set up logging for the test module."""
    logger.remove()
    logger.add(sys.stdout, level="DEBUG")

@pytest.fixture
def tweet_validator():
    """Fixture to create a TweetValidator instance."""
    return TweetValidator()

@pytest.fixture
def tweet_data():
    """Fixture to provide test data."""
    return {
        "tweet_id": "1841569771898450238",
        "expected_username": "getmasafi",
        "expected_created_at": "2024-10-02 13:03:00"
    }

def test_fetch_tweet(tweet_validator, tweet_data):
    """Test the fetch_tweet method of TweetValidator."""
    logger.info(f"Testing fetch_tweet with tweet ID: {tweet_data['tweet_id']}")

    result = tweet_validator.fetch_tweet(tweet_data['tweet_id'])
    logger.debug(f"Raw response from fetch_tweet: {result}")

    assert result is not None, "Failed to fetch tweet"
    assert 'data' in result, "Response doesn't contain 'data' key"
    assert 'tweetResult' in result['data'], "Response doesn't contain 'tweetResult' key"
    assert 'result' in result['data']['tweetResult'], "Response doesn't contain 'result' key"

    tweet_data_result = result['data']['tweetResult']['result']

    assert 'legacy' in tweet_data_result, "Tweet data doesn't contain 'legacy' key"
    assert 'full_text' in tweet_data_result['legacy'], "Tweet data doesn't contain 'full_text' key"
    assert 'created_at' in tweet_data_result['legacy'], "Tweet data doesn't contain 'created_at' key"

    assert 'core' in tweet_data_result, "Tweet data doesn't contain 'core' key"
    assert 'user_results' in tweet_data_result['core'], "Tweet data doesn't contain 'user_results' key"
    assert 'result' in tweet_data_result['core']['user_results'], "User data doesn't contain 'result' key"
    assert 'legacy' in tweet_data_result['core']['user_results']['result'], "User data doesn't contain 'legacy' key"
    assert 'screen_name' in tweet_data_result['core']['user_results']['result']['legacy'], "User data doesn't contain 'screen_name' key"

    logger.info(f"Tweet text: {tweet_data_result['legacy']['full_text']}")
    logger.info(f"Tweet created at: {tweet_data_result['legacy']['created_at']}")
    logger.info(f"Tweet author: {tweet_data_result['core']['user_results']['result']['legacy']['screen_name']}")

def test_validate_tweet(tweet_data):
    """Test the validate_tweet method of TweetValidator with correct username."""
    logger.info(f"Testing validate_tweet with tweet ID: {tweet_data['tweet_id']} and expected username: {tweet_data['expected_username']}")

    is_valid = validate_main(tweet_data['tweet_id'], tweet_data['expected_username'], tweet_data['expected_created_at'])

    assert is_valid, f"Tweet validation failed for tweet ID: {tweet_data['tweet_id']}"
    logger.info(f"Tweet validation successful for tweet ID: {tweet_data['tweet_id']}")

def test_validate_tweet_wrong_username(tweet_data):
    """Test the validate_tweet method of TweetValidator with incorrect username."""
    wrong_username = "wrongusername"
    logger.info(f"Testing validate_tweet with tweet ID: {tweet_data['tweet_id']} and wrong username: {wrong_username}")

    is_valid = validate_main(tweet_data['tweet_id'], wrong_username)

    assert not is_valid, f"Tweet validation unexpectedly passed for wrong username: {wrong_username}"
    logger.info(f"Tweet validation correctly failed for wrong username: {wrong_username}")
