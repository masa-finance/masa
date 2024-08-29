import functools
from .exceptions import MASAException, APIException

class ErrorHandler:
    def __init__(self, qc_manager):
        self.qc_manager = qc_manager

    def handle_error(self, func):
        """
        Decorator to handle errors in a function.

        :param func: The function to decorate.
        :return: The decorated function.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except MASAException as e:
                self.qc_manager.log_error(f"{type(e).__name__}: {str(e)}", error_info=e, context=func.__qualname__)
                raise
            except Exception as e:
                self.qc_manager.log_error(f"Unexpected error: {type(e).__name__}: {str(e)}", error_info=e, context=func.__qualname__)
                raise MASAException(f"Unexpected error in {func.__qualname__}: {str(e)}") from e
        return wrapper

    def handle_error_with_retry(self, config_key):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return self.qc_manager.execute_with_retry(
                    self._api_call_with_error_handling,
                    config_key,
                    func, *args, **kwargs
                )
            return wrapper
        return decorator

    def _api_call_with_error_handling(self, func, *args, **kwargs):
        try:
            self.qc_manager.log_debug(f"Executing function: {func.__qualname__}", context="ErrorHandler")
            return func(*args, **kwargs)
        except MASAException as e:
            self.qc_manager.log_debug(f"Caught MASAException: {type(e).__name__}: {str(e)}", context="ErrorHandler")
            raise
        except Exception as e:
            self.qc_manager.log_debug(f"Caught unexpected exception: {type(e).__name__}: {str(e)}", context="ErrorHandler")
            raise APIException(f"Unexpected error in API call: {str(e)}", status_code=None) from e