import inspect
from logging import Logger
from typing import Callable, Awaitable, Any, Sequence, Optional

from slack_bolt.kwargs_injection.async_utils import build_async_required_kwargs
from slack_bolt.logger import get_bolt_app_logger
from slack_bolt.request.async_request import AsyncBoltRequest
from slack_bolt.response import BoltResponse
from .async_middleware import AsyncMiddleware
from slack_bolt.util.utils import get_name_for_callable, get_arg_names_of_callable


class AsyncCustomMiddleware(AsyncMiddleware):
    app_name: str
    func: Callable[..., Awaitable[Any]]
    arg_names: Sequence[str]
    logger: Logger

    def __init__(
        self,
        *,
        app_name: str,
        func: Callable[..., Awaitable[Any]],
        base_logger: Optional[Logger] = None,
    ):
        self.app_name = app_name
        if inspect.iscoroutinefunction(func):
            self.func = func
        else:
            raise ValueError("Async middleware function must be an async function")

        self.arg_names = get_arg_names_of_callable(func)
        self.logger = get_bolt_app_logger(self.app_name, self.func, base_logger)

    async def async_process(
        self,
        *,
        req: AsyncBoltRequest,
        resp: BoltResponse,
        # As this method is not supposed to be invoked by bolt-python users,
        # the naming conflict with the built-in one affects
        # only the internals of this method
        next: Callable[[], Awaitable[BoltResponse]],
    ) -> BoltResponse:
        return await self.func(
            **build_async_required_kwargs(
                logger=self.logger,
                required_arg_names=self.arg_names,
                request=req,
                response=resp,
                next_func=next,
                this_func=self.func,
            )
        )

    @property
    def name(self) -> str:
        return f"AsyncCustomMiddleware(func={get_name_for_callable(self.func)})"
