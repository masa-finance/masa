"""
The `masa.connections` package contains modules for handling API connections.

This package includes the following modules:

- `APIConnection`: Provides a generic class for handling API connections and requests.
- `XTwitterConnection`: Provides a class for handling connections to the Twitter API through the MASA Oracle.
"""
from .api_connection import APIConnection
from .xtwitter_connection import XTwitterConnection

__all__ = [
    'APIConnection',
    'XTwitterConnection'
]