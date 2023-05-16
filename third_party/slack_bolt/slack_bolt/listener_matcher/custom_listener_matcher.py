from logging import Logger
from typing import Callable, Sequence, Optional

from slack_bolt.kwargs_injection import build_required_kwargs
from slack_bolt.logger import get_bolt_app_logger
from slack_bolt.request import BoltRequest
from slack_bolt.response import BoltResponse
from .listener_matcher import ListenerMatcher
from ..util.utils import get_arg_names_of_callable


class CustomListenerMatcher(ListenerMatcher):
    app_name: str
    func: Callable[..., bool]
    arg_names: Sequence[str]
    logger: Logger

    def __init__(self, *, app_name: str, func: Callable[..., bool], base_logger: Optional[Logger] = None):
        self.app_name = app_name
        self.func = func
        self.arg_names = get_arg_names_of_callable(func)
        self.logger = get_bolt_app_logger(self.app_name, self.func, base_logger)

    def matches(self, req: BoltRequest, resp: BoltResponse) -> bool:
        return self.func(
            **build_required_kwargs(
                logger=self.logger,
                required_arg_names=self.arg_names,
                request=req,
                response=resp,
                this_func=self.func,
            )
        )
