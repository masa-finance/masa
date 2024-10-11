import pytest
from masa_ai.tools.validator import TweetValidator
from masa_ai.tools.validator.main import main as validate_main
from loguru import logger
import sys

@pytest.fixture(scope="module", autouse=True)
def setup_logging():
    """Set up logging for the test module."""
    logger.remove()
    logger.add(sys.stdout, level="INFO")

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
        "expected_text": '''WE ARE LIVE ✨ Tune in to the @NEARProtocol Hackathon #AI AMA with Masa  ⬇️ https://t.co/gfM7yNAo2e''',
        "expected_timestamp": 1727899422
    }

def test_fetch_tweet(tweet_validator, tweet_data):
    """Test the fetch_tweet method of TweetValidator."""
    result = tweet_validator.fetch_tweet(tweet_data['tweet_id'])

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

    logger.debug(f"Tweet: {tweet_data_result}")
    logger.debug(f"Tweet created at: {tweet_data_result['legacy']['created_at']}")
    logger.debug(f"Tweet author: {tweet_data_result['core']['user_results']['result']['legacy']['screen_name']}")
    
    logger.success(f"Tweet text: {tweet_data_result['legacy']['full_text']}")
    logger.success(f"Successfully fetched tweet data for tweet {tweet_data['tweet_id']}")

def test_validate_tweet(tweet_data):
    """Test the validate_tweet method of TweetValidator with correct username."""
    is_valid = validate_main(tweet_data['tweet_id'], tweet_data['expected_username'], tweet_data['expected_text'], tweet_data['expected_timestamp'])
    assert is_valid, f"Tweet validation failed for tweet ID: {tweet_data['tweet_id']}"

def test_validate_tweet_wrong_username(tweet_data):
    """Test the validate_tweet method of TweetValidator with incorrect username."""
    wrong_username = "wrongusername"
    is_valid = validate_main(tweet_data['tweet_id'], wrong_username, tweet_data['expected_text'], tweet_data['expected_timestamp'])
    assert not is_valid, f"Tweet validation unexpectedly passed for wrong username: {wrong_username}"

def test_validate_tweet_wrong_text(tweet_data):
    """Test the validate_tweet method of TweetValidator with incorrect username."""
    wrong_text = "hello"
    is_valid = validate_main(tweet_data['tweet_id'], tweet_data['expected_username'], wrong_text, tweet_data['expected_timestamp'])
    assert not is_valid, f"Tweet validation unexpectedly passed for wrong text: {wrong_text}"

def test_validate_tweet_wrong_created_at(tweet_data):
    """Test the validate_tweet method of TweetValidator with incorrect username."""
    wrong_created_at = 1723829423
    is_valid = validate_main(tweet_data['tweet_id'], tweet_data['expected_username'], tweet_data['expected_text'], wrong_created_at)
    assert not is_valid, f"Tweet validation unexpectedly passed for wrong created_at: {wrong_created_at}"
