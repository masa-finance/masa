"""
Request Router module for the MASA project.

This module provides the RequestRouter class, which is responsible for
routing requests to the appropriate retriever based on the request parameters.
"""

import uuid
from tools.retrieve.retrieve_xtwitter import XTwitterRetriever
from tools.qc.qc_manager import QCManager
import traceback
from configs.config import global_settings
from datetime import datetime

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

    def __init__(self, qc_manager, state_manager):
        """
        Initialize the RequestRouter.

        Args:
            qc_manager (tools.qc.qc_manager.QCManager): Quality control manager for logging and error handling.
            state_manager (orchestration.state_manager.StateManager): Manager for handling request states.
        """
        self.qc_manager = qc_manager
        self.config = global_settings
        self.state_manager = state_manager
        self.retrievers = {}

    def route_request(self, request):
        """
        Route the request to the appropriate retriever based on the request parameters.

        Args:
            request (dict): Dictionary containing the request parameters.

        Returns:
            dict: The result of processing the request.

        Raises:
            ValueError: If an unknown retriever or endpoint is specified.
        """
        request_id = request['id']
        query = request['params'].get('query', 'N/A')
        self.qc_manager.log_debug(f"Request details: Query '{query}' {request}", context="RequestRouter")

        try:
            retriever_name = request['retriever']
            endpoint = request['endpoint']

            self.qc_manager.log_debug(f"Routing request: Query '{query}' (ID: {request_id}) to {retriever_name}")

            # Use get_retriever method to initialize the retriever
            retriever = self.get_retriever(retriever_name, request)
            self.qc_manager.log_debug(f"Retrieved retriever object for {retriever_name}", context="RequestRouter")

            if retriever_name == 'XTwitterRetriever':
                if endpoint == 'data/twitter/tweets/recent':
                    self.qc_manager.log_debug(f"Calling retrieve_tweets for request: Query '{query}' (ID: {request_id})", context="RequestRouter")
                    all_tweets, api_calls_count, records_fetched = retriever.retrieve_tweets(request)
                    result = {
                        'tweets_count': records_fetched,
                        'api_calls_count': api_calls_count,
                        'last_processed_time': datetime.now().isoformat()
                    }
                    self.qc_manager.log_debug(f"Completed request: Query '{query}' (ID: {request_id}). API calls: {api_calls_count}, Records fetched: {records_fetched}")
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

        Args:
            retriever_name (str): Name of the retriever.
            request (dict): Dictionary containing the request parameters.

        Returns:
            object: Initialized retriever object.

        Raises:
            ValueError: If an unknown retriever name is provided.
        """
        if retriever_name not in self.retrievers:
            if retriever_name == 'XTwitterRetriever':
                self.retrievers[retriever_name] = XTwitterRetriever(self.state_manager, request)
            else:
                raise ValueError(f"Unknown retriever: {retriever_name}")
        return self.retrievers[retriever_name]