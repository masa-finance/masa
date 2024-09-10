"""
Logging configuration module for the MASA project.

This module provides functions to set up loggers with colored output and
file rotation capabilities.
"""

import logging
from logging.handlers import RotatingFileHandler
from colorlog import ColoredFormatter

def setup_logger(name, log_file, level=logging.INFO, log_format=None, date_format=None, color_enabled=True):
    """
    Set up a logger with file and console handlers.

    :param name: Name of the logger
    :type name: str
    :param log_file: Path to the log file
    :type log_file: str
    :param level: Logging level, defaults to logging.INFO
    :type level: int, optional
    :param log_format: Custom log format, defaults to None
    :type log_format: str, optional
    :param date_format: Custom date format, defaults to None
    :type date_format: str, optional
    :param color_enabled: Enable color logging, defaults to True
    :type color_enabled: bool, optional
    :return: Configured logger
    :rtype: logging.Logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # File handler
    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(log_format or '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                       datefmt=date_format or '%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    if color_enabled:
        console_formatter = ColoredFormatter(
            "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s%(reset)s",
            datefmt=date_format or '%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
            secondary_log_colors={},
            style='%'
        )
    else:
        console_formatter = logging.Formatter(log_format or '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                              datefmt=date_format or '%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger