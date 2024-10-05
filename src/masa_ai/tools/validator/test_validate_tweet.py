import unittest
from masa_ai.tools.validator import TweetValidator
from masa_ai.tools.validator.main import main as validate_main
from loguru import logger
import sys

class TestTweetValidator(unittest.TestCase):
    """
    A test case class for the TweetValidator and main function.

    This class contains unit tests for the TweetValidator class and the main function,
    testing methods for fetching and validating tweets.
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up the test environment for all test methods in this class.

        This method removes all existing loggers and adds a new one that
        outputs to stdout at the DEBUG level.
        """
        logger.remove() 
        logger.add(sys.stdout, level="DEBUG")

    def setUp(self):
        """
        Set up the test fixture before each test method.

        This method initializes a TweetValidator instance and sets up
        test data (tweet ID and expected username) for use in the tests.
        """
        self.validator = TweetValidator()
        self.tweet_id = "1841569771898450238"
        self.expected_username = "getmasafi"

    def test_fetch_tweet(self):
        """
        Test the fetch_tweet method of TweetValidator.

        This method tests whether the fetch_tweet method correctly retrieves
        tweet data and whether the retrieved data has the expected structure.

        Returns:
            None

        Raises:
            AssertionError: If any of the assertions fail.
        """
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
        self.assertIn('screen_name', tweet_data['core']['user_results']['result']['legacy'], "User data doesn't contain 'screen_name' key")
        
        # Log some details for manual verification
        logger.info(f"Tweet text: {tweet_data['legacy']['full_text']}")
        logger.info(f"Tweet created at: {tweet_data['legacy']['created_at']}")
        logger.info(f"Tweet author: {tweet_data['core']['user_results']['result']['legacy']['screen_name']}")

    def test_validate_tweet(self):
        """
        Test the validate_tweet method of TweetValidator with correct username.

        This method tests whether the validate_tweet method correctly validates
        a tweet when given the correct username, using the main function.

        Returns:
            None

        Raises:
            AssertionError: If the validation fails unexpectedly.
        """
        logger.info(f"Testing validate_tweet with tweet ID: {self.tweet_id} and expected username: {self.expected_username}")

        is_valid = validate_main(self.tweet_id, self.expected_username)
        
        self.assertTrue(is_valid, f"Tweet validation failed for tweet ID: {self.tweet_id}")
        logger.info(f"Tweet validation successful for tweet ID: {self.tweet_id}")

    def test_validate_tweet_wrong_username(self):
        """
        Test the validate_tweet method of TweetValidator with incorrect username.

        This method tests whether the validate_tweet method correctly invalidates
        a tweet when given an incorrect username, using the main function.

        Returns:
            None

        Raises:
            AssertionError: If the validation passes unexpectedly.
        """
        wrong_username = "wrongusername"
        logger.info(f"Testing validate_tweet with tweet ID: {self.tweet_id} and wrong username: {wrong_username}")

        is_valid = validate_main(self.tweet_id, wrong_username)
        
        self.assertFalse(is_valid, f"Tweet validation unexpectedly passed for wrong username: {wrong_username}")
        logger.info(f"Tweet validation correctly failed for wrong username: {wrong_username}")

    def tearDown(self):
        """
        Clean up after each test method.

        This method ensures that all logging is completed after each test.
        """
        logger.complete()

def main():
    """
    Main function to run the test suite.

    This function sets up the test environment, creates a test suite,
    and runs the tests using a test runner.
    """
    # Set up logging
    logger.remove()
    logger.add(sys.stdout, level="DEBUG")

    # Create a test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTweetValidator)

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return the result (useful for CI/CD pipelines)
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(main())
