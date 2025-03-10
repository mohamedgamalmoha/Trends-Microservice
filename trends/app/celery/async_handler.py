import asyncio
from functools import wraps
from typing import Any, Callable, TypeVar, Coroutine, AsyncGenerator


T = TypeVar('T')  # Resource type (db, client, etc.)


class AsyncHandler:
    """
    Helper class for handling async operations in synchronous Celery task events.
    Works with any type of async generator or coroutine.
    """

    @staticmethod
    def run_async(coro: Coroutine[Any, Any, T]) -> T:
        """
        Run an async coroutine in a new event loop.

        Args:
            coro: The coroutine to run

        Returns:
            The result of the coroutine
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    @classmethod
    def async_event(cls, event_handler: Callable[..., Coroutine]):
        """
        Decorator to run an async event handler in a sync context.

        Args:
            - event_handler: The async event handler function

        Returns:
            - Sync version of the event handler
        """

        @wraps(event_handler)
        def wrapper(self, *args, **kwargs):
            return cls.run_async(event_handler(self, *args, **kwargs))

        return wrapper

    @classmethod
    def with_async_generator(cls, resource_provider: Callable[[], AsyncGenerator[T, None]]):
        """
        Decorator that provides a resource from an async generator to an event handler.

        Args:
            - resource_provider: Function that returns an async generator yielding a resource

        Returns:
            - Decorator function that wraps an async event handler
        """

        def decorator(event_handler: Callable):
            @wraps(event_handler)
            def wrapper(self, *args, **kwargs):
                resource_provider_result = resource_provider()

                # Extract resource from generator
                resource = cls.run_async(
                    cls._get_resource_from_generator(
                        resource_provider_result
                    )
                )

                try:
                    # Run the handler with the resource
                    return cls.run_async(event_handler(self, resource, *args, **kwargs))
                finally:
                    # No explicit cleanup needed as generator context manager handles it
                    ...

            return wrapper

        return decorator

    @staticmethod
    async def _get_resource_from_generator(resource_gen: AsyncGenerator[T, None]) -> T:
        """
        Extract a resource from an async generator.

        Args:
            - resource_gen: The async generator that yields a resource

        Returns:
            - The extracted resource
        """
        resource = await resource_gen.__anext__()
        return resource
