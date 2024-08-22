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

    def generate_request_id(self):
        """
        Generate a unique UUID for a request.

        :return: A string representation of a UUID.
        """
        return str(uuid.uuid4())

    def route_request(self, request):
        """
        Route the request to the appropriate retriever based on the request parameters.

        :param request: Dictionary containing the request parameters.
        """
        # Generate a UUID if the request doesn't have one
        if 'id' not in request:
            request['id'] = self.generate_request_id()

        retriever_name = request['retriever']
        endpoint = request['endpoint']
        request_id = request['id']

        self.logger.log_info(f"Processing request {request_id} for {retriever_name}")

        if retriever_name not in self.retrievers:
            # Initialize the retriever if it hasn't been initialized yet
            if retriever_name == 'XTwitterRetriever':
                self.retrievers[retriever_name] = XTwitterRetriever(self.logger, self.config, self.state_manager)
            # Add more retriever initialization conditions as needed

        retriever = self.retrievers[retriever_name]  # Get the initialized retriever object

        # Update the state to 'in_progress' before starting the retrieval
        self.state_manager.update_request_state(request_id, 'in_progress')

        if retriever_name == 'XTwitterRetriever':
            if endpoint == 'data/twitter/tweets/recent':
                retriever.retrieve_tweets([request])  # Pass the entire request dictionary as a list
            # Add more endpoint conditions as needed
        # Add more retriever conditions as needed

        # After the retrieval is complete, update the state to 'completed'
        self.state_manager.update_request_state(request_id, 'completed')

        self.logger.log_info(f"Completed request {request_id} for {retriever_name}")