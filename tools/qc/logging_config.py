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
from colorlog import ColoredFormatter
from configs.config import global_settings

def setup_logger(name):
    """
    Set up a logger with colored output based on global settings.

    :param name: The name of the logger.
    :type name: str
    :return: The configured logger.
    :rtype: logging.Logger
    """
    log_settings = global_settings.logging

    logger = logging.getLogger(name)
    log_level = getattr(logging, log_settings.LOG_LEVEL)
    logger.setLevel(log_level)

    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler()
        console_level = getattr(logging, log_settings.get('CONSOLE_LOG_LEVEL', log_settings.LOG_LEVEL))
        console_handler.setLevel(console_level)
        
        if log_settings.get('COLOR_ENABLED', True):
            formatter = ColoredFormatter(
                log_settings.LOG_FORMAT,
                datefmt=log_settings.LOG_DATE_FORMAT,
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                },
                reset=True,
                secondary_log_colors={}
            )
        else:
            formatter = logging.Formatter(log_settings.LOG_FORMAT, datefmt=log_settings.LOG_DATE_FORMAT)
        
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler
        if log_settings.get('LOG_FILE'):
            file_handler = logging.FileHandler(log_settings.LOG_FILE)
            file_level = getattr(logging, log_settings.get('FILE_LOG_LEVEL', log_settings.LOG_LEVEL))
            file_handler.setLevel(file_level)
            file_formatter = logging.Formatter(log_settings.LOG_FORMAT.replace('%(log_color)s', '').replace('%(reset)s', ''), 
                                               datefmt=log_settings.LOG_DATE_FORMAT)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

    return logger