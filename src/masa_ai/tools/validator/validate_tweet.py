import requests
import json
import uuid
import time
from urllib.parse import urlencode
from loguru import logger

BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"

class TweetValidator:
    def __init__(self):
        self.guest_token = None
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            "Authorization": f"Bearer {BEARER_TOKEN}",
        })
        logger.add("validate_tweet.log", level="DEBUG")

    def get_guest_token(self):
        try:
            response = self.session.post("https://api.twitter.com/1.1/guest/activate.json")
            response.raise_for_status()
            self.guest_token = response.json()["guest_token"]
        except requests.RequestException as e:
            logger.error(f"Error obtaining guest token: {e}")
            return None
        return self.guest_token

    def generate_client_transaction_id(self):
        return str(uuid.uuid4())

    def fetch_tweet(self, tweet_id):
        guest_token = self.get_guest_token()
        if not guest_token:
            logger.error("Failed to obtain guest token")
            return None

        url = "https://api.x.com/graphql/sCU6ckfHY0CyJ4HFjPhjtg/TweetResultByRestId"
        params = {
            "variables": json.dumps({
                "tweetId": tweet_id,
                "withCommunity": False,
                "includePromotedContent": False,
                "withVoice": False
            }),
            "features": json.dumps({
                "creator_subscriptions_tweet_preview_api_enabled": True,
                "communities_web_enable_tweet_community_results_fetch": True,
                "c9s_tweet_anatomy_moderator_badge_enabled": True,
                "articles_preview_enabled": True,
                "responsive_web_edit_tweet_api_enabled": True,
                "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
                "view_counts_everywhere_api_enabled": True,
                "longform_notetweets_consumption_enabled": True,
                "responsive_web_twitter_article_tweet_consumption_enabled": True,
                "tweet_awards_web_tipping_enabled": False,
                "creator_subscriptions_quote_tweet_preview_enabled": False,
                "freedom_of_speech_not_reach_fetch_enabled": True,
                "standardized_nudges_misinfo": True,
                "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
                "rweb_video_timestamps_enabled": True,
                "longform_notetweets_rich_text_read_enabled": True,
                "longform_notetweets_inline_media_enabled": True,
                "rweb_tipjar_consumption_enabled": True,
                "responsive_web_graphql_exclude_directive_enabled": True,
                "verified_phone_label_enabled": False,
                "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
                "responsive_web_graphql_timeline_navigation_enabled": True,
                "responsive_web_enhance_cards_enabled": False
            }),
            "fieldToggles": json.dumps({
                "withArticleRichContentState": True,
                "withArticlePlainText": False,
                "withGrokAnalyze": False,
                "withDisallowedReplyControls": False
            })
        }

        headers = {
            "Accept": "*/*",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Referer": "https://x.com/",
            "Content-Type": "application/json",
            "Origin": "https://x.com",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Sec-Ch-Ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"macOS"',
            "X-Guest-Token": guest_token,
            "X-Client-Transaction-Id": self.generate_client_transaction_id(),
            "X-Twitter-Active-User": "yes",
            "X-Twitter-Client-Language": "en-GB"
        }

        try:
            full_url = f"{url}?{urlencode(params)}"
            response = self.session.get(full_url, headers=headers)
            response.raise_for_status()
            logger.debug(f"Raw response from Twitter API: {response.text}")
            
            # Check if the response is valid JSON
            try:
                return response.json()
            except requests.exceptions.JSONDecodeError:
                logger.error(f"Invalid JSON response: {response.text}")
                return None

        except requests.RequestException as e:
            logger.error(f"Error fetching tweet: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status code: {e.response.status_code}")
                logger.error(f"Response content: {e.response.text}")
            else:
                logger.error("No response received from the server")
            return None

    def validate_tweet(self, tweet_id, tweet_json):
        fetched_data = self.fetch_tweet(tweet_id)
        if not fetched_data:
            logger.error(f"Failed to fetch tweet data for ID: {tweet_id}")
            return False

        try:
            fetched_tweet = fetched_data['data']['tweetResult']['result']
            
            # Validate tweet ID
            if fetched_tweet['rest_id'] != tweet_json['ID']:
                logger.error(f"Tweet ID mismatch: {fetched_tweet['rest_id']} != {tweet_json['ID']}")
                return False

            # Validate tweet author's username
            fetched_username = fetched_tweet['core']['user_results']['result']['legacy']['screen_name']
            if fetched_username != tweet_json['Username']:
                logger.error(f"Tweet author username mismatch: {fetched_username} != {tweet_json['Username']}")
                return False

            logger.info(f"Tweet validation successful for ID: {tweet_id}")
            return True

        except KeyError as e:
            logger.error(f"KeyError during tweet validation: {e}")
            return False

def main():
    validator = TweetValidator()
    tweet_id = "1842280371695612109"
    
    tweet_json = {
        "ConversationID": "1841568881716167072",
        "GIFs": None,
        "HTML": "<a href=\"https://twitter.com/NEARProtocol\">@NEARProtocol</a> Ready to start building innovative <a href=\"https://twitter.com/hashtag/AI\">#AI</a> Agents &amp; applications with Masa Data?<br><br>Check out our QuickStart Guide: <a href=\"https://docs.google.com/document/d/1uBE7Om78wdu-scFfo0Bm5r9nV5jyQkCx5ZdhXK-utpQ/edit\">https://t.co/PaGOvzY2x7</a><br><br>If you have questions - join our Discord channel. Our team is ready to assist you.<br><a href=\"https://discord.gg/ZdX3ah4v\">https://t.co/CwuzEWo9a6</a>",
        "Hashtags": ["AI"],
        "ID": "1842280371695612109",
        "InReplyToStatus": None,
        "InReplyToStatusID": "1841568881716167072",
        "IsPin": False,
        "IsQuoted": False,
        "IsReply": True,
        "IsRetweet": False,
        "IsSelfThread": False,
        "Likes": 6,
        "Mentions": [
            {
                "ID": "1031949518609121280",
                "Name": "NEAR Protocol",
                "Username": "NEARProtocol"
            }
        ],
        "Name": "Masa",
        "PermanentURL": "https://twitter.com/getmasafi/status/1842280371695612109",
        "Photos": None,
        "Place": None,
        "QuotedStatus": None,
        "QuotedStatusID": "",
        "Replies": 0,
        "RetweetedStatus": None,
        "RetweetedStatusID": "",
        "Retweets": 0,
        "SensitiveContent": False,
        "Text": "@NEARProtocol Ready to start building innovative #AI Agents &amp; applications with Masa Data?\n\nCheck out our QuickStart Guide: https://t.co/PaGOvzY2x7\n\nIf you have questions - join our Discord channel. Our team is ready to assist you.\nhttps://t.co/CwuzEWo9a6",
        "Thread": None,
        "TimeParsed": "2024-10-04T19:07:23Z",
        "Timestamp": 1728068843,
        "URLs": [
            "https://docs.google.com/document/d/1uBE7Om78wdu-scFfo0Bm5r9nV5jyQkCx5ZdhXK-utpQ/edit",
            "https://discord.gg/ZdX3ah4v"
        ],
        "UserID": "1419111693112676353",
        "Username": "getmasafi",
        "Videos": None,
        "Views": 221
    }
    
    is_valid = validator.validate_tweet(tweet_id, tweet_json)
    if is_valid:
        logger.info(f"Tweet {tweet_id} is valid.")
    else:
        logger.warning(f"Tweet {tweet_id} is not valid.")

if __name__ == "__main__":
    logger.add("tweet_scraper.log", rotation="10 MB")
    main()