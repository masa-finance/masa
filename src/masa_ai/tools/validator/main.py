from loguru import logger
from masa_ai.tools.validator.validate_tweet import TweetValidator

def main():
    """
    Main function to validate a tweet.

    This function creates a TweetValidator instance, validates a specific tweet,
    and logs the result.

    Returns:
        None
    """
    validator = TweetValidator()
    tweet_id = "1841569771898450238"
    expected_username = "getmasafi"
    
    is_valid = validator.validate_tweet(tweet_id, expected_username)
    if is_valid:
        logger.info(f"Tweet {tweet_id} is valid and posted by {expected_username}")
    else:
        logger.warning(f"Tweet {tweet_id} validation failed")

if __name__ == "__main__":
    logger.add("tweet_scraper.log", rotation="10 MB")
    main()