from abc import ABCMeta, abstractmethod
from typing import Callable, Awaitable, Optional

from slack_bolt.request.async_request import AsyncBoltRequest
from slack_bolt.response import BoltResponse


class AsyncMiddleware(metaclass=ABCMeta):
    """A middleware can process request data before other middleware and listener functions."""

    @abstractmethod
    async def async_process(
        self,
        *,
        req: AsyncBoltRequest,
        resp: BoltResponse,
        # As this method is not supposed to be invoked by bolt-python users,
        # the naming conflict with the built-in one affects
        # only the internals of this method
        next: Callable[[], Awaitable[BoltResponse]],
    ) -> Optional[BoltResponse]:
        """Processes a request data before other middleware and listeners.
        A middleware calls `next()` function if the chain should continue.

            @app.middleware
            async def simple_middleware(req, resp, next):
                # do something here
                await next()

        This `async_process(req, resp, next)` method is supposed to be invoked only inside bolt-python.
        If you want to avoid the name `next()` in your middleware functions, you can use `next_()` method instead.

            @app.middleware
            async def simple_middleware(req, resp, next_):
                # do something here
                await next_()

        Args:
            req: The incoming request
            resp: The response
            next: The function to tell the chain that it can continue

        Returns:
            Processed response (optional)
        """
        raise NotImplementedError()

    @property
    def name(self) -> str:
        """The name of this middleware"""
        return f"{self.__module__}.{self.__class__.__name__}"
