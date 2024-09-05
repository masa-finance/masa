"""
Package initialization file for masa.configs.

This file imports the necessary classes and functions from the config.py module
and specifies the names to be exported when using `from masa.configs import *`.
"""

from .config import initialize_config

__all__ = [
    'initialize_config'
]