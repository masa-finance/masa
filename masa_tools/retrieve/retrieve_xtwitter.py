from connections.xtwitter_connection import XTwitterConnection
from masa_tools.utils.data_storage import DataStorage
from masa_tools.qc.error_handler import ErrorHandler
import os
import json
import time
from datetime import datetime

class XTwitterRetriever:
    def __init__(self, logger, config):
        """
        Initialize the XTwitterRetriever with the necessary configurations.

        :param logger: The logger object.
        :param error_handler: The error handler object.
        :param config: The configuration object.
        """
        self.logger = logger
        self.config = config
        self.error_handler = ErrorHandler(self.logger)
        self.twitter_connection = XTwitterConnection()
        self.state_file = 'retriever_state.json'
        self.data_storage = DataStorage()

    @ErrorHandler.handle_error
    def retrieve_tweets(self, requests_list):
        """
        Retrieve tweets based on the provided list of requests.

        :param requests_list: A list of dictionaries containing the request parameters.
        """
        state = self._load_state()
        completed_requests = state.get('completed_requests', [])
        
        for request in requests_list:
            if request in completed_requests:
                self.logger.log_info(f"Skipping request {request} as it has already been completed.")
                continue

            params = request['params']  # Extract the 'params' dictionary from the request
            query = params['query']
            count = params['count']

            success = False
            attempts = 0
            while not success and attempts < self.config.get('max_retries', 3):
                data = {  # Use 'data' instead of 'json'
                    'query': query,
                    'count': count
                }
                response = self.twitter_connection.make_request('/data/twitter/tweets/recent', method='POST', data=data)
                self._handle_response(response, query)
                success = True
                completed_requests.append(request)
                self._save_state(completed_requests)

                if not success:
                    self.logger.log_warning(f"Request {request} failed. Retrying in {self.config.get('retry_delay', 60)} seconds...")
                    time.sleep(self.config.get('retry_delay', 60))
                    attempts += 1

            if not success:
                self.error_handler.raise_error("RetrievalError", f"Failed to process request {request} after {attempts} attempts.")

    @ErrorHandler.handle_error
    def _handle_response(self, response, query):
        """
        Handle the response from the Twitter API.

        :param response: The response object.
        :param query: The query used to retrieve the data.
        """
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:  # Check if 'data' key exists in the response
                tweets = json.dumps(data['data'], indent=4)  # Access 'data' instead of 'tweets'
                self.data_storage.save_data(tweets, 'xtwitter', query)
                self.logger.log_info(f"Successfully retrieved {len(data['data'])} tweets")
            else:
                self.error_handler.raise_error("MissingDataError", "The 'data' key is missing in the response.")
        else:
            self.error_handler.raise_error("RequestError", f"Failed to retrieve tweets. Status code: {response.status_code}")

    def _load_state(self):
        """
        Load the retriever state from the state file.
        """
        try:
            with open(self.state_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def _save_state(self, completed_requests):
        """
        Save the retriever state to the state file.

        :param completed_requests: A list of completed requests.
        """
        state = {
            'completed_requests': completed_requests,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(self.state_file, 'w') as file:
            json.dump(state, file, indent=4)