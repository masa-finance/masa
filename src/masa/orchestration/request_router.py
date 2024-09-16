"""
Request Router module for the MASA project.

This module provides the RequestRouter class, which is responsible for
routing requests to the appropriate retriever based on the request parameters.
"""

from ..tools.retrieve.retrieve_xtwitter import XTwitterRetriever
from ..tools.qc.qc_manager import QCManager
import traceback
from ..configs.config import global_settings

class RequestRouter:
    """
    Class for routing requests to the appropriate retriever based on the request parameters.

    This class manages the initialization of retrievers and directs requests
    to the appropriate retriever based on the request type and endpoint.

    Attributes:
        qc_manager (tools.qc.qc_manager.QCManager): Quality control manager for logging and error handling.
        config (dict): Configuration settings for the request router.
        state_manager (orchestration.state_manager.StateManager): Manager for handling request states.
        retrievers (dict): Dictionary to store initialized retriever objects.
    """

    def __init__(self, qc_manager: QCManager, state_manager):
        """
        Initialize the RequestRouter.

        :param qc_manager: Quality control manager for logging and error handling.
        :type qc_manager: tools.qc.qc_manager.QCManager
        :param state_manager: Manager for handling request states.
        :type state_manager: orchestration.state_manager.StateManager
        """
        self.qc_manager = qc_manager
        self.config = global_settings
        self.state_manager = state_manager
        self.retrievers = {}
    
    def route_request(self, request_id, request):
        """
        Route the request to the appropriate retriever based on the request parameters.

        :param request_id: The ID of the request.
        :type request_id: str
        :param request: Dictionary containing the request parameters.
        :type request: dict
        :return: The result of processing the request.
        :rtype: dict
        :raises ValueError: If an unknown retriever or endpoint is specified.
        """

        retriever_name = request['retriever']
        endpoint = request['endpoint']
        params = request['params']

        query = params.get('query', 'N/A')
        self.qc_manager.log_debug(f"Request details: Query '{query}' {request}", context="RequestRouter")

        try:
            self.qc_manager.log_debug(f"Routing request: {request_id} to {retriever_name} for endpoint {endpoint}", context="RequestRouter")

            if retriever_name == 'XTwitterRetriever':
                if endpoint == 'data/twitter/tweets/recent':
                    retriever = self.get_retriever(retriever_name, request)
                    self.qc_manager.log_debug(f"Calling retrieve_tweets for request: Query '{query}' (ID: {request_id})", context="RequestRouter")
                    
                    # Ensure 'query' and 'count' are present in the params
                    if 'query' not in params or 'count' not in params:
                        raise ValueError("Missing 'query' or 'count' parameter in the request")
                    
                    result = retriever.retrieve_tweets(request_id, params['query'], params['count'])
                    self.qc_manager.log_debug(f"Completed request: Query '{query}' (ID: {request_id}).")
                    return result
                else:
                    raise ValueError(f"Unknown endpoint for {retriever_name}: {endpoint}")
            else:
                raise ValueError(f"Unknown retriever: {retriever_name}")

        except Exception as e:
            self.qc_manager.log_error(f"Error in route_request for Query '{query}' (ID: {request_id}): {str(e)}", error_info=e, context="RequestRouter")
            self.qc_manager.log_error(f"Traceback: {traceback.format_exc()}", context="RequestRouter")
            raise

    def get_retriever(self, retriever_name, request):
        """
        Get the retriever object for a given retriever name.

        :param retriever_name: Name of the retriever.
        :type retriever_name: str
        :param request: Dictionary containing the request parameters.
        :type request: dict
        :return: Initialized retriever object.
        :rtype: object
        :raises ValueError: If an unknown retriever name is provided.
        """
        if retriever_name not in self.retrievers:
            if retriever_name == 'XTwitterRetriever':
                self.retrievers[retriever_name] = XTwitterRetriever(self.state_manager, request)
            else:
                raise ValueError(f"Unknown retriever: {retriever_name}")
        return self.retrievers[retriever_name]