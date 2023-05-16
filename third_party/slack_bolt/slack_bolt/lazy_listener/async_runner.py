from abc import abstractmethod, ABCMeta
from logging import Logger
from typing import Callable, Awaitable

from slack_bolt.lazy_listener.async_internals import to_runnable_function
from slack_bolt.request.async_request import AsyncBoltRequest


class AsyncLazyListenerRunner(metaclass=ABCMeta):
    logger: Logger

    @abstractmethod
    def start(self, function: Callable[..., Awaitable[None]], request: AsyncBoltRequest) -> None:
        """Starts a new lazy listener execution.

        Args:
            function: The function to run.
            request: The request to pass to the function. The object must be thread-safe.
        """
        raise NotImplementedError()

    async def run(self, function: Callable[..., Awaitable[None]], request: AsyncBoltRequest) -> None:
        """Synchronously run the function with a given request data.

        Args:
            function: The function to run.
            request: The request to pass to the function. The object must be thread-safe.
        """
        func = to_runnable_function(
            internal_func=function,
            logger=self.logger,
            request=request,
        )
        return await func()  # type: ignore
