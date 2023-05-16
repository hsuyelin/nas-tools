from abc import abstractmethod, ABCMeta
from typing import Callable, Tuple, Sequence, Optional

from slack_bolt.listener_matcher import ListenerMatcher
from slack_bolt.middleware import Middleware
from slack_bolt.request import BoltRequest
from slack_bolt.response import BoltResponse


class Listener(metaclass=ABCMeta):
    matchers: Sequence[ListenerMatcher]
    middleware: Sequence[Middleware]  # type: ignore
    ack_function: Callable[..., BoltResponse]
    lazy_functions: Sequence[Callable[..., None]]
    auto_acknowledgement: bool

    def matches(
        self,
        *,
        req: BoltRequest,
        resp: BoltResponse,
    ) -> bool:
        is_matched: bool = False
        for matcher in self.matchers:
            is_matched = matcher.matches(req, resp)
            if not is_matched:
                return is_matched
        return is_matched

    def run_middleware(
        self,
        *,
        req: BoltRequest,
        resp: BoltResponse,
    ) -> Tuple[Optional[BoltResponse], bool]:
        """Runs a middleware.

        Args:
            req: The incoming request
            resp: The current response

        Returns:
            A tuple of the processed response and a flag indicating termination
        """
        for m in self.middleware:
            middleware_state = {"next_called": False}

            def next_():
                middleware_state["next_called"] = True

            resp = m.process(req=req, resp=resp, next=next_)
            if not middleware_state["next_called"]:
                # next() was not called in this middleware
                return (resp, True)
        return (resp, False)

    @abstractmethod
    def run_ack_function(self, *, request: BoltRequest, response: BoltResponse) -> Optional[BoltResponse]:
        """Runs all the registered middleware and then run the listener function.

        Args:
            request: The incoming request
            response: The current response

        Returns:
            The processed response
        """
        raise NotImplementedError()
