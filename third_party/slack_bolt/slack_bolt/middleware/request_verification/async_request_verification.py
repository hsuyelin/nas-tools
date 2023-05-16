from typing import Callable, Awaitable

from slack_bolt.middleware import RequestVerification
from slack_bolt.middleware.async_middleware import AsyncMiddleware
from slack_bolt.request.async_request import AsyncBoltRequest
from slack_bolt.response import BoltResponse


class AsyncRequestVerification(RequestVerification, AsyncMiddleware):
    """Verifies an incoming request by checking the validity of
    `x-slack-signature`, `x-slack-request-timestamp`, and its body data.

    Refer to https://api.slack.com/authentication/verifying-requests-from-slack for details.
    """

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
        if self._can_skip(req.mode, req.body):
            return await next()

        body = req.raw_body
        timestamp = req.headers.get("x-slack-request-timestamp", ["0"])[0]
        signature = req.headers.get("x-slack-signature", [""])[0]
        if self.verifier.is_valid(body, timestamp, signature):
            return await next()
        else:
            self._debug_log_error(signature, timestamp, body)
            return self._build_error_response()
