from abc import ABCMeta, abstractmethod
from logging import Logger
from typing import Callable, Dict, Any, Awaitable, Optional

from slack_bolt.kwargs_injection.async_utils import build_async_required_kwargs
from slack_bolt.request.async_request import AsyncBoltRequest
from slack_bolt.response import BoltResponse
from slack_bolt.util.utils import get_arg_names_of_callable


class AsyncMiddlewareErrorHandler(metaclass=ABCMeta):
    @abstractmethod
    async def handle(
        self,
        error: Exception,
        request: AsyncBoltRequest,
        response: Optional[BoltResponse],
    ) -> None:
        """Handles an unhandled exception.

        Args:
            error: The raised exception.
            request: The request.
            response: The response.
        """
        raise NotImplementedError()


class AsyncCustomMiddlewareErrorHandler(AsyncMiddlewareErrorHandler):
    def __init__(self, logger: Logger, func: Callable[..., Awaitable[Optional[BoltResponse]]]):
        self.func = func
        self.logger = logger
        self.arg_names = get_arg_names_of_callable(func)

    async def handle(
        self,
        error: Exception,
        request: AsyncBoltRequest,
        response: Optional[BoltResponse],
    ) -> None:
        kwargs: Dict[str, Any] = build_async_required_kwargs(
            required_arg_names=self.arg_names,
            logger=self.logger,
            error=error,
            request=request,
            response=response,
            next_keys_required=False,
        )
        returned_response = await self.func(**kwargs)
        if returned_response is not None and isinstance(returned_response, BoltResponse):
            response.status = returned_response.status
            response.headers = returned_response.headers
            response.body = returned_response.body


class AsyncDefaultMiddlewareErrorHandler(AsyncMiddlewareErrorHandler):
    def __init__(self, logger: Logger):
        self.logger = logger

    async def handle(
        self,
        error: Exception,
        request: AsyncBoltRequest,
        response: Optional[BoltResponse],
    ):
        message = f"Failed to run a middleware function (error: {error})"
        self.logger.exception(message)
