import functools
from .exceptions import MASAException, APIException

class ErrorHandler:
    def __init__(self, qc_manager):
        self.qc_manager = qc_manager

    def handle_error(self, custom_handlers=None):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if custom_handlers and type(e) in custom_handlers:
                        return custom_handlers[type(e)](e)
                    return self._default_error_handler(e, func.__qualname__)
            return wrapper
        return decorator

    def _default_error_handler(self, e, func_name):
        if isinstance(e, MASAException):
            self.qc_manager.log_error(f"{type(e).__name__} in {func_name}: {str(e)}", error_info=e)
        else:
            self.qc_manager.log_error(f"Unexpected error in {func_name}: {str(e)}", error_info=e)
        raise

    def handle_error_with_retry(self, config_key):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return self.qc_manager.execute_with_retry(func, config_key, *args, **kwargs)
            return wrapper
        return decorator