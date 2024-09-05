"""
Logging configuration module for the MASA project.

This module provides functions to set up loggers with colored output based on
the global settings defined in the project's configuration.

Functions:
    setup_logger(name: str) -> logging.Logger:
        Set up a logger with the specified name and colored output based on
        the global settings.
"""

import logging
from logging.handlers import RotatingFileHandler
import colorlog
from configs.config import global_settings
import os

def setup_logger(name):
    """
    Set up a logger with colored output based on global settings.

    This function configures a logger with the specified name based on the global
    settings defined in the project's configuration. It sets up console and file
    handlers, applies formatting, and returns the configured logger.

    :param name: The name of the logger.
    :type name: str
    :return: The configured logger.
    :rtype: logging.Logger

    Example:
        >>> logger = setup_logger('my_logger')
        >>> logger.info('This is an informational message')
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    # Check if we're building docs
    if 'READTHEDOCS' in os.environ or 'BUILDING_DOCS' in os.environ:
        # Use a NullHandler when building docs
        logger.addHandler(logging.NullHandler())
    else:
        # Get settings
        log_settings = global_settings.get('logging', {})
        
        # Use an absolute path for the log file within the src/masa path
        default_log_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'masa.log')
        log_file = log_settings.get('LOG_FILE', default_log_path)
        
        # Ensure the log directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        log_format = log_settings.get('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        date_format = log_settings.get('LOG_DATE_FORMAT', '%Y-%m-%d %H:%M:%S')
        console_level = getattr(logging, log_settings.get('CONSOLE_LOG_LEVEL', 'INFO'))
        file_level = getattr(logging, log_settings.get('FILE_LOG_LEVEL', 'DEBUG'))
        color_enabled = log_settings.get('COLOR_ENABLED', True)

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level)

        # File Handler
        file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
        file_handler.setLevel(file_level)

        if color_enabled:
            formatter = colorlog.ColoredFormatter(log_format, date_format)
        else:
            formatter = logging.Formatter(log_format, date_format)

        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger