import argparse
from loguru import logger
from masa_ai.tools.validator.validate_tweet import TweetValidator
from typing import List, Optional

def main(tweet_id: str, expected_name: str, expected_username: str, expected_text: str, expected_timestamp: int, expected_hashtags: Optional[List[str]] = None) -> bool:
    """Validate a tweet and log the result.

    Creates a TweetValidator instance, validates a specific tweet,
    and logs the result.

    Args:
        tweet_id (str): The ID of the tweet to validate.
        expected_username (str): The expected username of the tweet author.
        expected_timestamp (str): The expected created_at of the tweet.
        expected_hashtags (Optional[List[str]]): The expected hashtags of the tweet.
    Returns:
        bool: True if the tweet is valid and posted by the expected username,
            False otherwise.
    """
    validator = TweetValidator()
    is_valid = validator.validate_tweet(tweet_id, expected_name, expected_username, expected_text, expected_timestamp, expected_hashtags)
    return is_valid

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate a tweet")
    parser.add_argument("tweet_id", help="The ID of the tweet to validate")
    parser.add_argument("expected_name", help="The expected name of the tweet author")
    parser.add_argument("expected_username", help="The expected username of the tweet author")
    parser.add_argument("expected_text", help="The expected text of the tweet")
    parser.add_argument("expected_timestamp", help="The expected timestamp of the tweet")
    parser.add_argument("--expected_hashtags", nargs='*', help="The expected hashtags of the tweet", default=None)
    parser.add_argument("--log-file", default="tweet_scraper.log", help="Path to the log file")
    parser.add_argument("--log-rotation", default="10 MB", help="Log rotation size")
    
    args = parser.parse_args()

    logger.add(args.log_file, rotation=args.log_rotation)
    
    result = main(args.tweet_id, args.expected_name, args.expected_username, args.expected_text, args.expected_timestamp, args.expected_hashtags)