from masa_tools.retrieve.retrieve_xtwitter import XTwitterRetriever
from masa_tools.qc.logging import Logger
from masa_tools.qc.error_handler import ErrorHandler
from masa.configs.config import XTwitterConfig

def main():
    """
    Main function to run the XTwitterRetriever.
    """
    logger = Logger(__name__)  # Initialize the logger
    error_handler = ErrorHandler(logger)  # Initialize the error handler
    config = XTwitterConfig().get_config()  # Initialize the config

    retriever = XTwitterRetriever(logger, error_handler, config)  # Pass the objects to the retriever

    # Define the list of requests
    requests_list = [
        {
            'query': 'your_query_1',
            'count': 100
        },
        {
            'query': 'your_query_2',
            'count': 200
        }
        # Add more requests as needed
    ]

    # Call the retrieve_tweets method with the requests list
    retriever.retrieve_tweets(requests_list)

if __name__ == '__main__':
    main()