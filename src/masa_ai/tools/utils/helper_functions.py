"""
Helper functions module for the MASA project.

This module contains utility functions used throughout the MASA application.
These functions provide common operations that are not specific to any particular
module but are useful across the project.
"""

from urllib.parse import urljoin

def format_url(base_url, endpoint):
    """
    Format the URL by properly joining the base URL and endpoint.
    
    This function ensures that the base URL and endpoint are correctly
    joined, handling cases where the base URL might or might not end
    with a slash, and the endpoint might or might not start with a slash.

    Args:
        base_url (str): The base URL of the API.
        endpoint (str): The specific endpoint to be accessed.

    Returns:
        str: A properly formatted URL.

    Example:
        >>> format_url("http://api.example.com", "/v1/data")
        "http://api.example.com/v1/data"
    """
    # Ensure base_url ends with a slash and endpoint doesn't start with a slash
    base_url = base_url.rstrip('/') + '/'
    endpoint = endpoint.lstrip('/')
    return urljoin(base_url, endpoint)
