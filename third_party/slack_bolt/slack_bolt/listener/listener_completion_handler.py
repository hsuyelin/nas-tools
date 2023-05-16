from abc import ABCMeta, abstractmethod
from logging import Logger
from typing import Callable, Dict, Any, Optional

from slack_bolt.kwargs_injection import build_required_kwargs
from slack_bolt.request.request import BoltRequest
from slack_bolt.response.response import BoltResponse
from slack_bolt.util.utils import get_arg_names_of_callable


class ListenerCompletionHandler(metaclass=ABCMeta):
    @abstractmethod
    def handle(
        self,
        request: BoltRequest,
        response: Optional[BoltResponse],
    ) -> None:
        """Do something extra after the listener execution

        Args:
            request: The request.
            response: The response.
        """
        raise NotImplementedError()


class CustomListenerCompletionHandler(ListenerCompletionHandler):
    def __init__(self, logger: Logger, func: Callable[..., None]):
        self.func = func
        self.logger = logger
        self.arg_names = get_arg_names_of_callable(func)

    def handle(
        self,
        request: BoltRequest,
        response: Optional[BoltResponse],
    ):
        kwargs: Dict[str, Any] = build_required_kwargs(
            required_arg_names=self.arg_names,
            logger=self.logger,
            request=request,
            response=response,
            next_keys_required=False,
        )
        self.func(**kwargs)


class DefaultListenerCompletionHandler(ListenerCompletionHandler):
    def __init__(self, logger: Logger):
        self.logger = logger

    def handle(
        self,
        request: BoltRequest,
        response: Optional[BoltResponse],
    ):
        pass
