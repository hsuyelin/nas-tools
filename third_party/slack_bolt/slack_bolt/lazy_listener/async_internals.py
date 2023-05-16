from functools import wraps
from logging import Logger
from typing import Callable, Awaitable

from slack_bolt.kwargs_injection.async_utils import build_async_required_kwargs
from slack_bolt.request.async_request import AsyncBoltRequest
from slack_bolt.util.utils import get_arg_names_of_callable


async def to_runnable_function(
    internal_func: Callable[..., Awaitable[None]],
    logger: Logger,
    request: AsyncBoltRequest,
):
    arg_names = get_arg_names_of_callable(internal_func)

    @wraps(internal_func)
    async def request_wired_wrapper() -> None:
        try:
            await internal_func(
                **build_async_required_kwargs(
                    logger=logger,
                    required_arg_names=arg_names,
                    request=request,
                    response=None,
                    this_func=internal_func,
                )
            )
        except Exception as e:
            logger.error(f"Failed to run an internal function ({e})")

    return await request_wired_wrapper()
