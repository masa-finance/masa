from masa_tools.retrieve.retrieve_xtwitter import XTwitterRetriever
from masa_tools.qc.logging import Logger
from masa_tools.qc.error_handler import ErrorHandler
from configs.config import XTwitterConfig

def main(requests_list):
    """
    Main function to run the specified retrievers based on the requests list.

    :param requests_list: List of requests specifying the retriever, endpoint, and parameters.
    """
    logger = Logger(__name__)  # Initialize the logger
    # error_handler = ErrorHandler(logger)  # Initialize the error handler
    config = XTwitterConfig().get_config()  # Initialize the config

    retrievers = {}  # Dictionary to store initialized retriever objects

    for request in requests_list:
        retriever_name = request['retriever']
        endpoint = request['endpoint']
        params = request['params']

        if retriever_name not in retrievers:
            # Initialize the retriever if it hasn't been initialized yet
            if retriever_name == 'XTwitterRetriever':
                retrievers[retriever_name] = XTwitterRetriever(logger, config)
            # Add more retriever initialization conditions as needed

        retriever = retrievers[retriever_name]  # Get the initialized retriever object

        if retriever_name == 'XTwitterRetriever':
            if endpoint == '/data/tweets':
                retriever.retrieve_tweets([request])  # Pass the entire request dictionary as a list
            # Add more endpoint conditions as needed
        # Add more retriever conditions as needed

if __name__ == '__main__':
    # Define the list of requests
    requests_list = [
        {
            'retriever': 'XTwitterRetriever',
            'endpoint': '/data/tweets',
            'params': {
                'query': '#Bitcoin',
                'count': 10
            }
        },
        {
            'retriever': 'XTwitterRetriever',
            'endpoint': '/data/tweets',
            'params': {
                'query': '@brendanplayford',
                'count': 20
            }
        }
        # Add more requests as needed
    ]

    main(requests_list)  # Call the main function with the requests list