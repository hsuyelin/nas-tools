from logging import Logger
from typing import Callable, Optional

from slack_bolt.logger import get_bolt_logger
from slack_bolt.middleware.middleware import Middleware
from slack_bolt.request import BoltRequest
from slack_bolt.response import BoltResponse


class SslCheck(Middleware):  # type: ignore
    verification_token: Optional[str]
    logger: Logger

    def __init__(
        self,
        verification_token: Optional[str] = None,
        base_logger: Optional[Logger] = None,
    ):
        """Handles `ssl_check` requests.
        Refer to https://api.slack.com/interactivity/slash-commands for details.

        Args:
            verification_token: The verification token to check
                (optional as it's already deprecated - https://api.slack.com/authentication/verifying-requests-from-slack#verification_token_deprecation)
            base_logger: The base logger
        """  # noqa: E501
        self.verification_token = verification_token
        self.logger = get_bolt_logger(SslCheck, base_logger=base_logger)

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
        if self._is_ssl_check_request(req.body):
            if self._verify_token_if_needed(req.body):
                return self._build_error_response()
            return self._build_success_response()
        else:
            return next()

    # -----------------------------------------

    @staticmethod
    def _is_ssl_check_request(body: dict):
        return "ssl_check" in body and body["ssl_check"] == "1"

    def _verify_token_if_needed(self, body: dict):
        return self.verification_token and self.verification_token == body["token"]

    @staticmethod
    def _build_success_response() -> BoltResponse:
        return BoltResponse(status=200, body="")

    @staticmethod
    def _build_error_response() -> BoltResponse:
        return BoltResponse(status=401, body={"error": "invalid verification token"})
