import requests
import json
import uuid
from urllib.parse import urlencode
from datetime import datetime
import time
from loguru import logger
from masa_ai.tools.validator.config import BEARER_TOKEN, USER_AGENT, API_URLS, FEATURES, FIELD_TOGGLES, HEADERS

class TweetValidator:
    """Validate tweets and fetch tweet data from the Twitter API.

    This class provides methods to obtain a guest token, fetch tweet data,
    and validate if a tweet is posted by an expected user.

    Attributes:
        guest_token (str): The guest token for API authentication.
        session (requests.Session): A session object for making HTTP requests.
    """

    def __init__(self):
        """Initialize the TweetValidator with default settings and a new session."""
        self.guest_token = None
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Authorization": f"Bearer {BEARER_TOKEN}",
        })
        logger.add("validate_tweet.log", level="DEBUG")

    def get_guest_token(self):
        """Obtain a guest token from the Twitter API.

        Returns:
            str: The obtained guest token if successful, None otherwise.

        Raises:
            requests.RequestException: If there's an error in obtaining the guest token.
        """
        try:
            response = self.session.post(API_URLS["guest_token"])
            response.raise_for_status()
            self.guest_token = response.json()["guest_token"]
        except requests.RequestException as e:
            logger.error(f"Error obtaining guest token: {e}")
            return None
        return self.guest_token

    def generate_client_transaction_id(self):
        """Generate a unique client transaction ID.

        Returns:
            str: A UUID4 string to be used as a client transaction ID.
        """
        return str(uuid.uuid4())

    def fetch_tweet(self, tweet_id):
        """Fetch tweet data from the Twitter API for a given tweet ID.

        Args:
            tweet_id (str): The ID of the tweet to fetch.

        Returns:
            dict: The JSON response containing tweet data if successful, None otherwise.

        Raises:
            requests.RequestException: If there's an error in fetching the tweet data.
        """
        guest_token = self.get_guest_token()
        if not guest_token:
            logger.error("Failed to obtain guest token")
            return None

        params = {
            "variables": json.dumps({
                "tweetId": tweet_id,
                "withCommunity": False,
                "includePromotedContent": False,
                "withVoice": False
            }),
            "features": json.dumps(FEATURES),
            "fieldToggles": json.dumps(FIELD_TOGGLES)
        }

        headers = HEADERS.copy()
        headers.update({
            "X-Guest-Token": guest_token,
            "X-Client-Transaction-Id": self.generate_client_transaction_id(),
        })

        try:
            full_url = f"{API_URLS['tweet_by_id']}?{urlencode(params)}"
            response = self.session.get(full_url, headers=headers)
            response.raise_for_status()
            # logger.debug(f"Raw response from Twitter API: {response.text}")
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching tweet: {e}")
            if hasattr(e, 'response'):
                logger.error(f"Response status code: {e.response.status_code}")
                logger.error(f"Response content: {e.response.text}")
            return None

    def validate_tweet(self, tweet_id: str, expected_username: str, expected_timestamp: int) -> bool:
        """Validate that the tweet with the given ID is made by the expected username, at the expected time.

        Args:
            tweet_id (str): The ID of the tweet to validate.
            expected_username (str): The expected username of the tweet author.
            expected_timestamp (int): The expected timestamp of the tweet.

        Returns:
            bool: True if the tweet's username matches the expected username, False otherwise.

        Raises:
            Exception: If an unexpected error occurs during validation.
        """
        try:
            tweet_data = self.fetch_tweet(tweet_id)
            if not tweet_data:
                logger.error(f"Tweet data could not be fetched for tweet ID {tweet_id}")
                return False
            
            # logger.info(f"Tweet data: {tweet_data}")
            actual_username = tweet_data.get('data', {}).get('tweetResult', {}).get('result', {}).get('core', {}).get('user_results', {}).get('result', {}).get('legacy', {}).get('screen_name')
            actual_created_at_date_string = tweet_data.get('data', {}).get('tweetResult', {}).get('result', {}).get('legacy', {}).get('created_at')

            if actual_username is None:
                logger.error(f"Could not extract username from tweet data for tweet ID: {tweet_id}")
                return False
            if actual_created_at_date_string is None:
                logger.error(f"Could not extract created_at from tweet data for tweet ID: {tweet_id}")
                return False
        
            # convert the created at from date_string to timestamp for comparison
            date_format = "%a %b %d %H:%M:%S %z %Y"
            dt = datetime.strptime(actual_created_at_date_string, date_format)
            actual_timestamp = int(dt.timestamp())

            logger.info(f"Actual timestamp converted: {actual_timestamp}")

            if actual_username.lower() != expected_username.lower():
                logger.info(f"Tweet {tweet_id} is not posted by the expected user: {expected_username}")
                return False
            if actual_timestamp != expected_timestamp:
                logger.info(f"Tweet {tweet_id} is not posted at the expected time: {expected_timestamp}")
                return False
            else:
                logger.info(f"Tweet {tweet_id} is valid!")
                return True
        except Exception as e:
            logger.error(f"An error occurred during validation: {e}")
            return False