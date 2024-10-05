"""Provide functionality for validating and fetching data from various sources.

This module contains classes and utilities for validating and fetching data,
particularly from social media platforms like Twitter.

Classes:
    TweetValidator: Validate and fetch tweet data.

Attributes:
    BEARER_TOKEN (str): The bearer token for API authentication.
    USER_AGENT (str): The user agent string for HTTP requests.
    API_URLS (dict): A dictionary of API endpoint URLs.
    FEATURES (dict): A dictionary of feature flags.
    FIELD_TOGGLES (dict): A dictionary of field toggle settings.
    HEADERS (dict): A dictionary of HTTP headers for API requests.
"""

from .validate_tweet import TweetValidator
from .config import BEARER_TOKEN, USER_AGENT, API_URLS, FEATURES, FIELD_TOGGLES, HEADERS
