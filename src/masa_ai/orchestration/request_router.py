"""
Request Router module for the MASA project.

This module provides the RequestRouter class, which is responsible for
routing requests to the appropriate scraper based on the request parameters.
"""

from ..tools.scrape.scrape_xtwitter import XTwitterScraper
from ..tools.qc.qc_manager import QCManager
import traceback
from ..configs.config import global_settings

class RequestRouter:
    """
    Class for routing requests to the appropriate scraper based on the request parameters.

    This class manages the initialization of scrapers and directs requests
    to the appropriate scraper based on the request type and endpoint.

    Attributes:
        qc_manager (tools.qc.qc_manager.QCManager): Quality control manager for logging and error handling.
        config (dict): Configuration settings for the request router.
        state_manager (orchestration.state_manager.StateManager): Manager for handling request states.
        scrapers (dict): Dictionary to store initialized scraper objects.
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
        self.scrapers = {}
    
    def route_request(self, request_id, request):
        """
        Route the request to the appropriate scraper based on the request parameters.

        :param request_id: The ID of the request.
        :type request_id: str
        :param request: Dictionary containing the request parameters.
        :type request: dict
        :return: The result of processing the request.
        :rtype: dict
        :raises ValueError: If an unknown scraper or endpoint is specified.
        """

        scraper_name = request['scraper']
        endpoint = request['endpoint']
        params = request['params']

        query = params.get('query', 'N/A')
        self.qc_manager.log_debug(f"Request details: Query '{query}' {request}", context="RequestRouter")

        try:
            self.qc_manager.log_debug(f"Routing request: {request_id} to {scraper_name} for endpoint {endpoint}", context="RequestRouter")

            if scraper_name == 'XTwitterScraper':
                if endpoint == 'data/twitter/tweets/recent':
                    scraper = self.get_scraper(scraper_name, request)
                    self.qc_manager.log_debug(f"Calling scrape_tweets for request: Query '{query}' (ID: {request_id})", context="RequestRouter")
                    
                    # Ensure 'query' and 'count' are present in the params
                    if 'query' not in params or 'count' not in params:
                        raise ValueError("Missing 'query' or 'count' parameter in the request")
                    
                    result = scraper.scrape_tweets(request_id, params['query'], params['count'])
                    self.qc_manager.log_debug(f"Completed request: Query '{query}' (ID: {request_id}).")
                    return result
                else:
                    raise ValueError(f"Unknown endpoint for {scraper_name}: {endpoint}")
            else:
                raise ValueError(f"Unknown scraper: {scraper_name}")

        except Exception as e:
            self.qc_manager.log_error(f"Error in route_request for Query '{query}' (ID: {request_id}): {str(e)}", error_info=e, context="RequestRouter")
            self.qc_manager.log_error(f"Traceback: {traceback.format_exc()}", context="RequestRouter")
            raise

    def get_scraper(self, scraper_name, request):
        """
        Get the scraper object for a given scraper name.

        :param scraper_name: Name of the scraper.
        :type scraper_name: str
        :param request: Dictionary containing the request parameters.
        :type request: dict
        :return: Initialized scraper object.
        :rtype: object
        :raises ValueError: If an unknown scraper name is provided.
        """
        if scraper_name not in self.scrapers:
            if scraper_name == 'XTwitterScraper':
                self.scrapers[scraper_name] = XTwitterScraper(self.state_manager, request)
            else:
                raise ValueError(f"Unknown scraper: {scraper_name}")
        return self.scrapers[scraper_name]