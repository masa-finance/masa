import uuid
from masa_tools.retrieve.retrieve_xtwitter import XTwitterRetriever

class RequestRouter:
    """
    Class for routing requests to the appropriate retriever based on the request parameters.
    """

    def __init__(self, logger, config, state_manager):
        """
        Initialize the RequestRouter.

        :param logger: Logger object for logging messages.
        :param config: Configuration object containing necessary settings.
        :param state_manager: StateManager object for managing request states.
        """
        self.logger = logger
        self.config = config
        self.state_manager = state_manager
        self.retrievers = {}  # Dictionary to store initialized retriever objects

    def route_request(self, request):
        """
        Route the request to the appropriate retriever based on the request parameters.

        :param request: Dictionary containing the request parameters.
        """
        retriever_name = request['retriever']
        endpoint = request['endpoint']
        request_id = request['id']

        self.logger.log_info(f"Routing request {request_id} to {retriever_name}")

        if retriever_name not in self.retrievers:
            # Initialize the retriever if it hasn't been initialized yet
            if retriever_name == 'XTwitterRetriever':
                self.retrievers[retriever_name] = XTwitterRetriever(self.logger, self.config, self.state_manager)
            # Add more retriever initialization conditions as needed
        
        retriever = self.retrievers[retriever_name]  # Get the initialized retriever object

        # Update the state to 'in_progress' before starting the retrieval
        self.state_manager.update_request_state(request_id, 'in_progress')

        try:
            if retriever_name == 'XTwitterRetriever':
                if endpoint == 'data/twitter/tweets/recent':
                    retriever.retrieve_tweets(request)
                else:
                    raise ValueError(f"Unknown endpoint for {retriever_name}: {endpoint}")
            else:
                raise ValueError(f"Unknown retriever: {retriever_name}")

            # After the retrieval is complete, update the state to 'completed'
            self.state_manager.update_request_state(request_id, 'completed')
            self.logger.log_info(f"Completed request {request_id} for {retriever_name}")
        except Exception as e:
            self.logger.log_error(f"Error processing request {request_id}: {str(e)}")
            self.state_manager.update_request_state(request_id, 'failed', {'error': str(e)})
            raise  # Re-raise the exception to be handled by the RequestManager

    def get_retriever(self, retriever_name):
        """
        Get the retriever object for a given retriever name.

        :param retriever_name: Name of the retriever.
        :return: Initialized retriever object.
        """
        if retriever_name not in self.retrievers:
            if retriever_name == 'XTwitterRetriever':
                self.retrievers[retriever_name] = XTwitterRetriever(self.logger, self.config, self.state_manager)
            # Add more retriever initialization conditions as needed
        return self.retrievers[retriever_name]