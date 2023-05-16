from concurrent.futures import Executor
from logging import Logger
from typing import Callable

from slack_bolt.lazy_listener.internals import build_runnable_function
from slack_bolt.lazy_listener.runner import LazyListenerRunner
from slack_bolt.request import BoltRequest


class ThreadLazyListenerRunner(LazyListenerRunner):
    logger: Logger

    def __init__(
        self,
        logger: Logger,
        executor: Executor,
    ):
        self.logger = logger
        self.executor = executor

    def start(self, function: Callable[..., None], request: BoltRequest) -> None:
        self.executor.submit(
            build_runnable_function(
                func=function,
                logger=self.logger,
                request=request,
            )
        )
