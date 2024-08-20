from masa.configs.config import XTwitterConfig
from masa.connections.xtwitter_connection import XTwitterConnection
from masa_tools.qc.logging import Logger
from masa_tools.qc.error_handler import ErrorHandler
import os
import json

logger = Logger(__name__)
error_handler = ErrorHandler(logger)
config = XTwitterConfig().get_config()

def retrieve_tweets():
    """
    Retrieve tweets using the Twitter API.
    """
    try:
        base_url = config.get('api_endpoint')
        bearer_token = config.get('TWITTER_BEARER_TOKEN')
        
        twitter_connection = XTwitterConnection(base_url, bearer_token)
        
        query = config.get('query')
        max_results = config.get('max_results')
        start_time = config.get('start_time')
        end_time = config.get('end_time')
        
        params = {
            'query': query,
            'max_results': max_results,
            'start_time': start_time,
            'end_time': end_time,
            'tweet.fields': 'created_at,text,author_id,public_metrics'
        }
        
        response = twitter_connection.make_request('', params=params)
        
        if response.status_code == 200:
            data = response.json()
            tweets = data['data']
            
            data_directory = config.get('data_directory')
            os.makedirs(data_directory, exist_ok=True)
            
            file_path = os.path.join(data_directory, 'tweets.json')
            with open(file_path, 'w') as file:
                json.dump(tweets, file, indent=4)
            
            logger.log_info(f"Successfully retrieved {len(tweets)} tweets and saved to {file_path}")
        else:
            error_handler.raise_error("RequestError", f"Failed to retrieve tweets. Status code: {response.status_code}")
    except Exception as e:
        error_handler.handle_error(retrieve_tweets)