from masa_tools.retrieve.retrieve_xtwitter import XTwitterRetriever
from masa_tools.qc.logging import Logger
from masa_tools.qc.error_handler import ErrorHandler
from configs.config import XTwitterConfig
from masa_tools.utils.state_manager import StateManager
from masa_tools.utils.request_router import RequestRouter

def main(requests_list):
    """
    Main function to run the specified retrievers based on the requests list.

    :param requests_list: List of requests specifying the retriever, endpoint, and parameters.
    """
    logger = Logger(__name__)  # Initialize the logger
    config = XTwitterConfig().get_config()  # Initialize the config
    state_manager = StateManager('data/state_manager.json')  # Initialize the StateManager

    router = RequestRouter(logger, config, state_manager)  # Initialize the RequestRouter

    for request in requests_list:
        router.route_request(request)  # Route each request using the RequestRouter

if __name__ == '__main__':
    # Define the list of requests
    requests_list = [
        {
            'retriever': 'XTwitterRetriever',
            'endpoint': 'data/twitter/tweets/recent',
            'params': {
                'query': '#KamalaHarris',
                'count': 50
            }
        },
        {
            'retriever': 'XTwitterRetriever',
            'endpoint': 'data/twitter/tweets/recent',
            'params': {
                'query': '@brendanplayford',
                'count': 50
            }
        }
        # Add more requests as needed
    ]

    main(requests_list)  # Call the main function with the requests list