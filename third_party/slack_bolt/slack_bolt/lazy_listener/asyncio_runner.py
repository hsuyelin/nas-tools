import asyncio
from logging import Logger
from typing import Callable, Awaitable

from slack_bolt.lazy_listener.async_internals import to_runnable_function
from slack_bolt.lazy_listener.async_runner import AsyncLazyListenerRunner
from slack_bolt.request.async_request import AsyncBoltRequest


class AsyncioLazyListenerRunner(AsyncLazyListenerRunner):
    logger: Logger

    def __init__(
        self,
        logger: Logger,
    ):
        self.logger = logger

    def start(self, function: Callable[..., Awaitable[None]], request: AsyncBoltRequest) -> None:
        asyncio.ensure_future(
            to_runnable_function(
                internal_func=function,
                logger=self.logger,
                request=request,
            )
        )
