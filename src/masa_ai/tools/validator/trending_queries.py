import requests
from loguru import logger
from masa_ai.tools.validator.config import BEARER_TOKEN, USER_AGENT, API_URLS, HEADERS

class TrendingQueries:
    """Fetch trending topics from the Twitter API.

    This class provides methods to obtain a guest token and fetch the highest trending topic.

    Attributes:
        guest_token (str): The guest token for API authentication.
        session (requests.Session): A session object for making HTTP requests.
    """

    def __init__(self):
        """Initialize the TweetTrends with default settings and a new session."""
        self.guest_token = None
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Authorization": f"Bearer {BEARER_TOKEN}",
        })

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

    def fetch(self):
        """Fetch the highest trending topic from the Twitter API.

        Returns:
            str: The name of the highest trending topic if successful, None otherwise.

        Raises:
            requests.RequestException: If there's an error in fetching the trending topics.
        """
        guest_token = self.get_guest_token()
        if not guest_token:
            logger.error("Failed to obtain guest token")
            return None

        headers = HEADERS.copy()
        headers.update({
            "X-Guest-Token": guest_token,
        })

        try:
            response = self.session.get(API_URLS["trending_topics"], headers=headers)
            response.raise_for_status()
            response_json = response.json()
            trends_data = dict(response_json[0]).get("trends", [])
            sorted_trends = sorted(trends_data, key=lambda x: x.get('tweet_volume') or 0, reverse=True)
            trends = [{'query': trend['name'], 'volume': trend['tweet_volume']} for trend in sorted_trends if trend['tweet_volume'] and trend['tweet_volume'] > 0]
            return trends
        except requests.RequestException as e:
            logger.error(f"Error fetching trending topics: {e}")
            if hasattr(e, 'response'):
                logger.error(f"Response status code: {e.response.status_code}")
                logger.error(f"Response content: {e.response.text}")
            return None 