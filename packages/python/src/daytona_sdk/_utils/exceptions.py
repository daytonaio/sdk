import json
import functools
from typing import Callable, Optional
from daytona_api_client.exceptions import OpenApiException


class DaytonaException(Exception):
    """Base exception for Daytona SDK."""
    pass


def intercept_exceptions(message_prefix: Optional[str] = ""):
    """Decorator to intercept exceptions, process them, and optionally add a message prefix.
    If the exception is an OpenApiException, it will be processed to extract the most meaningful exception message.

    Args:
        message_prefix (Optional[str]): Custom message prefix for the exception.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except OpenApiException as e:
                message = _get_open_api_exception_message(e)

                raise DaytonaException(f"{message_prefix}{message}") from None
            except Exception as e:
                if message_prefix:
                    message = f"{message_prefix}{str(e)}"
                    raise DaytonaException(message)
                raise DaytonaException(str(e))

        return wrapper
    return decorator


def _get_open_api_exception_message(exception: OpenApiException) -> str:
    """Process API exceptions to extract the most meaningful error message.

    This method examines the exception's body attribute and attempts to extract
    the most informative error message using the following logic:
    1. If the body is missing or empty, returns the original exception
    2. If the body contains valid JSON with a 'message' field, uses that message
    3. If the body is not valid JSON or does not contain a 'message' field, uses the raw body string

    Args:
        exception: The OpenApiException to process

    Returns:
        Exception with processed message
    """
    if not hasattr(exception, 'body') or not exception.body:
        return str(exception)

    body_str = str(exception.body)
    try:
        data = json.loads(body_str)
        message = data.get('message', body_str) if isinstance(
            data, dict) else body_str
    except json.JSONDecodeError:
        message = body_str

    return message
