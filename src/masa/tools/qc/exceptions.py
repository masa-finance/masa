"""
Custom exceptions for the MASA project.

This module defines custom exceptions used throughout the MASA project
for more specific error handling and reporting.

Exceptions:
    MASAException: Base exception for MASA project.
    APIException: Exception for API-related errors.
    NetworkException: Exception for network-related errors.
    NoWorkersAvailableException: Exception for no workers available errors.
    GatewayTimeoutException: Exception for gateway timeout errors.
    RateLimitException: Exception for rate limiting errors.
    AuthenticationException: Exception for authentication errors.
    DataProcessingException: Exception for data processing errors.
    ConfigurationException: Exception for configuration errors.
"""

class MASAException(Exception):
    """
    Base exception for MASA project.

    Args:
        message (str): The error message.
        status_code (int, optional): The HTTP status code.
        error_info (Any, optional): Additional error information.
    """
    def __init__(self, message, status_code=None, error_info=None):
        """
        Initialize the MASAException.

        Args:
            message (str): The error message.
            status_code (int, optional): The HTTP status code.
            error_info (Any, optional): Additional error information.
        """
        super().__init__(message)
        self.status_code = status_code
        self.error_info = error_info

class APIException(MASAException):
    """Exception for API-related errors."""

class NetworkException(APIException):
    """Exception for network-related errors."""

class NoWorkersAvailableException(APIException):
    """Exception for no workers available errors."""

class GatewayTimeoutException(APIException):
    """Exception for gateway timeout errors."""

class RateLimitException(APIException):
    """Exception for rate limiting errors."""

class AuthenticationException(APIException):
    """Exception for authentication errors."""

class DataProcessingException(MASAException):
    """Exception for data processing errors."""

class ConfigurationException(MASAException):
    """Exception for configuration errors."""

