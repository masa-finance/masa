class MASAException(Exception):
    """Base exception for MASA project"""

class APIException(MASAException):
    """Base exception for API-related errors"""

class NetworkException(APIException):
    """Exception for network-related errors"""

class RateLimitException(APIException):
    """Exception for rate limiting"""

class AuthenticationException(APIException):
    """Exception for authentication errors"""

class DataProcessingException(MASAException):
    """Exception for data processing errors"""

class ConfigurationException(MASAException):
    """Exception for configuration errors"""
