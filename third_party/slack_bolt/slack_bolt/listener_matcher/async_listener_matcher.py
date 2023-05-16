from abc import abstractmethod, ABCMeta

from slack_bolt.request.async_request import AsyncBoltRequest
from slack_bolt.response import BoltResponse
from slack_bolt.util.utils import get_arg_names_of_callable


class AsyncListenerMatcher(metaclass=ABCMeta):
    @abstractmethod
    async def async_matches(self, req: AsyncBoltRequest, resp: BoltResponse) -> bool:
        """Matches against the request and returns True if matched.

        Args:
            req: The request
            resp: The response

        Returns:
            True if matched
        """
        raise NotImplementedError()


from logging import Logger
from typing import Callable, Awaitable, Sequence, Optional

from slack_bolt.kwargs_injection.async_utils import build_async_required_kwargs
from slack_bolt.logger import get_bolt_app_logger
from slack_bolt.request.async_request import AsyncBoltRequest
from slack_bolt.response import BoltResponse


class AsyncCustomListenerMatcher(AsyncListenerMatcher):
    app_name: str
    func: Callable[..., Awaitable[bool]]
    arg_names: Sequence[str]
    logger: Logger

    def __init__(self, *, app_name: str, func: Callable[..., Awaitable[bool]], base_logger: Optional[Logger] = None):
        self.app_name = app_name
        self.func = func
        self.arg_names = get_arg_names_of_callable(func)
        self.logger = get_bolt_app_logger(self.app_name, self.func, base_logger)

    async def async_matches(self, req: AsyncBoltRequest, resp: BoltResponse) -> bool:
        return await self.func(
            **build_async_required_kwargs(
                logger=self.logger,
                required_arg_names=self.arg_names,
                request=req,
                response=resp,
                this_func=self.func,
            )
        )


builtin_async_listener_matcher_classes = [
    AsyncCustomListenerMatcher,
]
for cls in builtin_async_listener_matcher_classes:
    AsyncListenerMatcher.register(cls)
