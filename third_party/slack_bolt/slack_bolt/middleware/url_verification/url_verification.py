from logging import Logger
from typing import Callable, Optional

from slack_bolt.logger import get_bolt_logger
from slack_bolt.middleware.middleware import Middleware
from slack_bolt.request import BoltRequest
from slack_bolt.response import BoltResponse


class UrlVerification(Middleware):  # type: ignore
    def __init__(self, base_logger: Optional[Logger] = None):
        """Handles url_verification requests.

        Refer to https://api.slack.com/events/url_verification for details.

        Args:
            base_logger: The base logger
        """
        self.logger = get_bolt_logger(UrlVerification, base_logger=base_logger)

    def process(
        self,
        *,
        req: BoltRequest,
        resp: BoltResponse,
        # As this method is not supposed to be invoked by bolt-python users,
        # the naming conflict with the built-in one affects
        # only the internals of this method
        next: Callable[[], BoltResponse],
    ) -> BoltResponse:
        if self._is_url_verification_request(req.body):
            return self._build_success_response(req.body)
        else:
            return next()

    # -----------------------------------------

    @staticmethod
    def _is_url_verification_request(body: dict) -> bool:
        return body is not None and body.get("type") == "url_verification"

    @staticmethod
    def _build_success_response(body: dict) -> BoltResponse:
        return BoltResponse(status=200, body={"challenge": body.get("challenge")})
