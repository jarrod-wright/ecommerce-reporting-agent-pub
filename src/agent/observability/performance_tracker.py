import functools
import time

import structlog


def timing_decorator(func):
    """Decorator to log execution time of functions."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()

        duration_ms = (end_time - start_time) * 1000

        logger = structlog.get_logger()
        logger.info(
            "Function execution time",
            func_name=func.__name__,
            duration_ms=duration_ms
        )

        return result

    return wrapper
