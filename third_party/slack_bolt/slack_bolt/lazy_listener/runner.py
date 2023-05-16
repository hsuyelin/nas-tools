from abc import abstractmethod, ABCMeta
from logging import Logger
from typing import Callable

from slack_bolt.lazy_listener.internals import build_runnable_function
from slack_bolt.request import BoltRequest


class LazyListenerRunner(metaclass=ABCMeta):
    logger: Logger

    @abstractmethod
    def start(self, function: Callable[..., None], request: BoltRequest) -> None:
        """Starts a new lazy listener execution.

        Args:
            function: The function to run.
            request: The request to pass to the function. The object must be thread-safe.
        """
        raise NotImplementedError()

    def run(self, function: Callable[..., None], request: BoltRequest) -> None:
        """Synchronously runs the function with a given request data.

        Args:
            function: The function to run.
            request: The request to pass to the function. The object must be thread-safe.
        """
        build_runnable_function(
            func=function,
            logger=self.logger,
            request=request,
        )()
