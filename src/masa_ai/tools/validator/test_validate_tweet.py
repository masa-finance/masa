import unittest
from masa_ai.tools.validator.validate_tweet import TweetValidator
from loguru import logger
import sys

class TestTweetValidator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logger.remove()  # Remove default logger
        logger.add(sys.stdout, level="DEBUG")  # Add stdout logger for immediate visibility

    def setUp(self):
        self.validator = TweetValidator()
        self.tweet_id = "1841569771898450238"

    def test_fetch_tweet(self):
        logger.info(f"Testing fetch_tweet with tweet ID: {self.tweet_id}")

        result = self.validator.fetch_tweet(self.tweet_id)
        logger.debug(f"Raw response from fetch_tweet: {result}")

        # Check if we got a result
        self.assertIsNotNone(result, "Failed to fetch tweet")
        
        # Check if the result contains the expected data structure
        self.assertIn('data', result, "Response doesn't contain 'data' key")
        self.assertIn('tweetResult', result['data'], "Response doesn't contain 'tweetResult' key")
        self.assertIn('result', result['data']['tweetResult'], "Response doesn't contain 'result' key")
        
        tweet_data = result['data']['tweetResult']['result']
        
        # Check for specific tweet details
        self.assertIn('legacy', tweet_data, "Tweet data doesn't contain 'legacy' key")
        self.assertIn('full_text', tweet_data['legacy'], "Tweet data doesn't contain 'full_text' key")
        self.assertIn('created_at', tweet_data['legacy'], "Tweet data doesn't contain 'created_at' key")
        
        # Check for user details
        self.assertIn('core', tweet_data, "Tweet data doesn't contain 'core' key")
        self.assertIn('user_results', tweet_data['core'], "Tweet data doesn't contain 'user_results' key")
        self.assertIn('result', tweet_data['core']['user_results'], "User data doesn't contain 'result' key")
        self.assertIn('legacy', tweet_data['core']['user_results']['result'], "User data doesn't contain 'legacy' key")
        self.assertIn('name', tweet_data['core']['user_results']['result']['legacy'], "User data doesn't contain 'name' key")
        
        # Log some details for manual verification
        logger.info(f"Tweet text: {tweet_data['legacy']['full_text']}")
        logger.info(f"Tweet created at: {tweet_data['legacy']['created_at']}")
        logger.info(f"Tweet author: {tweet_data['core']['user_results']['result']['legacy']['name']}")

        # After all assertions, log a summary of the tweet data
        if result and 'data' in result and 'tweetResult' in result['data'] and 'result' in result['data']['tweetResult']:
            tweet_data = result['data']['tweetResult']['result']
            logger.info("Tweet verification successful. Summary:")
            logger.info(f"Tweet ID: {self.tweet_id}")
            logger.info(f"Tweet text: {tweet_data['legacy']['full_text']}")
            logger.info(f"Tweet created at: {tweet_data['legacy']['created_at']}")
            logger.info(f"Tweet author: {tweet_data['core']['user_results']['result']['legacy']['name']}")
        else:
            logger.error(f"Failed to verify tweet with ID: {self.tweet_id}")

    def tearDown(self):
        # Ensure all logs are written
        logger.complete()

if __name__ == '__main__':
    unittest.main()
