import uuid
from masa_tools.retrieve.retrieve_xtwitter import XTwitterRetriever
from masa_tools.qc.qc_manager import QCManager
import traceback
from configs.config import load_configs

class RequestRouter:
    """
    Class for routing requests to the appropriate retriever based on the request parameters.
    """

    def __init__(self, qc_manager, state_manager):
        """
        Initialize the RequestRouter.

        :param qc_manager: QCManager object for quality control.
        :param state_manager: StateManager object for managing request states.
        """
        self.qc_manager = qc_manager
        self.config = load_configs()  # Load configurations
        self.state_manager = state_manager
        self.retrievers = {}  # Dictionary to store initialized retriever objects

    def route_request(self, request):
        """
        Route the request to the appropriate retriever based on the request parameters.

        :param request: Dictionary containing the request parameters.
        """
        request_id = request['id']
        self.qc_manager.debug(f"Routing request with ID: {request_id}", context="RequestRouter")
        self.qc_manager.debug(f"Request details: {request}", context="RequestRouter")

        try:
            retriever_name = request['retriever']
            endpoint = request['endpoint']

            self.qc_manager.debug(f"Routing request {request_id} to {retriever_name}")

            if retriever_name not in self.retrievers:
                self.qc_manager.debug(f"Initializing retriever: {retriever_name}", context="RequestRouter")
                if retriever_name == 'XTwitterRetriever':
                    # Pass the entire request to the XTwitterRetriever
                    self.retrievers[retriever_name] = XTwitterRetriever(self.state_manager, request)
                else:
                    raise ValueError(f"Unknown retriever: {retriever_name}")

            retriever = self.retrievers[retriever_name]
            self.qc_manager.debug(f"Retrieved retriever object for {retriever_name}", context="RequestRouter")

            if retriever_name == 'XTwitterRetriever':
                if endpoint == 'data/twitter/tweets/recent':
                    self.qc_manager.debug(f"Calling retrieve_tweets for request {request_id}", context="RequestRouter")
                    all_tweets, api_calls_count, records_fetched = retriever.retrieve_tweets(request)
                    self.qc_manager.debug(f"Completed request {request_id}. API calls: {api_calls_count}, Records fetched: {records_fetched}")
                else:
                    raise ValueError(f"Unknown endpoint for {retriever_name}: {endpoint}")
            else:
                raise ValueError(f"Unknown retriever: {retriever_name}")

            self.qc_manager.debug(f"Completed request {request_id} for {retriever_name}")
            self.qc_manager.debug(f"------------------------------------------------")
        except Exception as e:
            self.qc_manager.debug(f"Error in route_request for {request_id}: {str(e)}", context="RequestRouter")
            self.qc_manager.debug(f"Traceback: {traceback.format_exc()}", context="RequestRouter")
            raise

    def get_retriever(self, retriever_name):
        """
        Get the retriever object for a given retriever name.

        :param retriever_name: Name of the retriever.
        :return: Initialized retriever object.
        """
        if retriever_name not in self.retrievers:
            if retriever_name == 'XTwitterRetriever':
                self.retrievers[retriever_name] = XTwitterRetriever(self.config, self.state_manager)
            # Add more retriever initialization conditions as needed
        return self.retrievers[retriever_name]