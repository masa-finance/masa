"""
This module contains helper functions used throughout the application.
"""

# Add helper functions here as needed

from urllib.parse import urljoin

def format_url(base_url, endpoint):
    """
    Format the URL by properly joining the base URL and endpoint.
    
    :param base_url: The base URL of the API
    :param endpoint: The specific endpoint to be accessed
    :return: A properly formatted URL
    """
    # Ensure base_url ends with a slash and endpoint doesn't start with a slash
    base_url = base_url.rstrip('/') + '/'
    endpoint = endpoint.lstrip('/')
    return urljoin(base_url, endpoint)
