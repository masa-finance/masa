from masa_tools.retrieve.retrieve_xtwitter import XTwitterRetriever

class RequestRouter:
    """
    Class for routing requests to the appropriate retriever based on the request parameters.
    """

    def __init__(self, logger, config):
        """
        Initialize the RequestRouter.

        :param logger: Logger object for logging messages.
        :param config: Configuration object containing necessary settings.
        """
        self.logger = logger
        self.config = config
        self.retrievers = {}  # Dictionary to store initialized retriever objects

    def route_request(self, request):
        """
        Route the request to the appropriate retriever based on the request parameters.

        :param request: Dictionary containing the request parameters.
        """
        retriever_name = request['retriever']
        endpoint = request['endpoint']
        params = request['params']

        if retriever_name not in self.retrievers:
            # Initialize the retriever if it hasn't been initialized yet
            if retriever_name == 'XTwitterRetriever':
                self.retrievers[retriever_name] = XTwitterRetriever(self.logger, self.config)
            # Add more retriever initialization conditions as needed

        retriever = self.retrievers[retriever_name]  # Get the initialized retriever object

        if retriever_name == 'XTwitterRetriever':
            if endpoint == 'data/twitter/tweets/recent':
                retriever.retrieve_tweets([request])  # Pass the entire request dictionary as a list
            # Add more endpoint conditions as needed
        # Add more retriever conditions as needed