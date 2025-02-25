import inspect
import functools
from typing import Optional, Any, Callable, Coroutine


def safe_call(func: Optional[Callable[..., Coroutine | None]] = None, *,
              on_error: Optional[Callable[[Exception, tuple, dict], Any]] = None) \
        -> Callable[..., Coroutine | None] | None:
    """
    A decorator that safely calls a function, handling exceptions by either returning a custom error result or None.

    If the function is a coroutine (async function), the decorator will handle it asynchronously.
    If the function is synchronous, it will be handled synchronously.

    Args:
        - func: The function to be wrapped. If None, this decorator can be used without arguments.
        - on_error: An optional callback that will be invoked when an exception occurs.
                  The callback receives the exception, the arguments, and the keyword arguments passed to the function.

    Returns:
        - A decorated function that either returns the result of the original function or handles exceptions based on `on_error`.
    """

    def decorator(fn: Callable[..., Coroutine | None]) -> Callable[..., Coroutine | None]:
        """
        A decorator that wraps the function to handle exceptions and execute `on_error` callback if provided.

        Args:
            - fn: The function to be wrapped by the decorator.

        Returns:
            - A wrapper function that executes the original function and handles exceptions.
        """

        @functools.wraps(fn)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Optional[Any]:
            """
            Synchronous wrapper for the decorated function. Executes the function and handles exceptions.

            Args:
                - *args: Positional arguments passed to the original function.
                - **kwargs: Keyword arguments passed to the original function.

            Returns:
                - The result of the function if successful, or None if an error occurs.
            """
            try:
                result = fn(*args, **kwargs)  # Call the function with provided arguments
                return result
            except Exception as e:
                # Handle exception by calling the `on_error` callback if it exists
                if on_error:
                    return on_error(e, args, kwargs)
            return None  # Return None if an exception occurs and no `on_error` callback is provided

        @functools.wraps(fn)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Coroutine | None:
            """
            Asynchronous wrapper for the decorated function. Executes the async function and handles exceptions.

            Args:
                - *args: Positional arguments passed to the original async function.
                - **kwargs: Keyword arguments passed to the original async function.

            Returns:
                - The result of the async function if successful, or None if an error occurs.
            """
            try:
                result = await fn(*args, **kwargs)  # Call the async function with provided arguments
                return result
            except Exception as e:
                # Handle exception by calling the `on_error` callback if it exists
                if on_error:
                    return on_error(e, args, kwargs)

        # If the function is a coroutine, use the async wrapper, otherwise use the sync wrapper
        if inspect.iscoroutinefunction(fn):
            return async_wrapper

        return sync_wrapper

    # If `func` is provided, apply the decorator immediately
    if func is None:
        return decorator  # Return the decorator to be applied later

    return decorator(func)  # If `func` is provided, apply the decorator to `func`
