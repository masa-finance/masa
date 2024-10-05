import requests
import json
from loguru import logger
from urllib.parse import urlencode

def fetch_data(url, params, headers):
    try:
        full_url = f"{url}?{urlencode(params)}"
        
        # Perform OPTIONS request
        options_headers = {
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization,content-type,x-client-transaction-id,x-guest-token,x-twitter-active-user,x-twitter-client-language",
            "Origin": "https://x.com",
            "Referer": "https://x.com/",
        }
        options_response = requests.options(full_url, headers={**headers, **options_headers})
        options_response.raise_for_status()
        
        # Perform GET request
        response = requests.get(full_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching data: {e}")
        return None

def save_data(data, filename):
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Data saved to {filename}")
    except IOError as e:
        logger.error(f"Error saving data: {e}")

def main():
    url = "https://api.x.com/graphql/sCU6ckfHY0CyJ4HFjPhjtg/TweetResultByRestId"
    params = {
        "variables": json.dumps({
            "tweetId": "1841569771898450238",
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
        "Authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Content-Type": "application/json",
        "Referer": "https://x.com/",
        "Origin": "https://x.com",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "X-Client-Transaction-Id": "2CcG/qS2JKKY/KwqisnYylcp7KUTvNW0Qe2Z1qW/KCAT7aDZ8RRDpMVjLrcz5FYVRtwjaNpNKIimUpu72Ewa8+aGtRqH2w",
        "X-Guest-Token": "1842316243820511492",
        "X-Twitter-Active-User": "yes",
        "X-Twitter-Client-Language": "en-GB",
    }

    data = fetch_data(url, params, headers)
    
    if data:
        save_data(data, "tweet_data.json")
    else:
        logger.warning("No data fetched. Check the error logs for details.")

if __name__ == "__main__":
    logger.add("tweet_scraper.log", rotation="10 MB")
    main()