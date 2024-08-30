class MASAException(Exception):
    """Base exception for MASA project"""
    def __init__(self, message, status_code=None, error_info=None):
        """
        Initialize the MASAException.

        :param message: The error message.
        :param status_code: The HTTP status code (default: None).
        :param error_info: Additional error information (default: None).
        """
        super().__init__(message)
        self.status_code = status_code
        self.error_info = error_info

class APIException(MASAException):
    """Base exception for API-related errors"""
    pass

class NetworkException(APIException):
    """Exception for network-related errors"""

class RateLimitException(APIException):
    """Exception for rate limiting"""
    pass

class AuthenticationException(APIException):
    """Exception for authentication errors"""

class DataProcessingException(MASAException):
    """Exception for data processing errors"""

class ConfigurationException(MASAException):
    """Exception for configuration errors"""

