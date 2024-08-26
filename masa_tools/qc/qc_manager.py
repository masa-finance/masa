# masa/masa_tools/qc/qc_manager.py

from .logging import Logger
from .error_handler import ErrorHandler

class QCManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(QCManager, cls).__new__(cls)
            cls._instance.logger = Logger()
            cls._instance.error_handler = ErrorHandler()
        return cls._instance

    def log_error(self, message, error_info=None, context=None):
        self.logger.log_error(message, error_info, context)

    def log_info(self, message, context=None):
        self.logger.log_info(message, context)

    def handle_error(self, func):
        return self.error_handler.handle_error(func)

    def handle_error_with_retry(self, retry_policy, config):
        return self.error_handler.handle_error_with_retry(retry_policy, config)

    def debug(self, message, context=None):
        """
        Log a debug message.

        Args:
            message (str): The debug message to log.
            context (str, optional): The context or source of the debug message. Defaults to None.
        """
        self.logger.log_debug(message, context)

    def set_debug(self, enabled: bool):
        """
        Enable or disable debug logging.

        Args:
            enabled (bool): True to enable debug logging, False to disable.
        """
        self.logger.set_debug(enabled)