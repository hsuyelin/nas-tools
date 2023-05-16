from logging import Logger
from typing import Callable, Awaitable, Optional

from slack_bolt.logger import get_bolt_logger
from slack_bolt.middleware.authorization.async_authorization import AsyncAuthorization
from slack_bolt.request.async_request import AsyncBoltRequest
from slack_bolt.response import BoltResponse
from slack_sdk.web.async_slack_response import AsyncSlackResponse
from slack_sdk.errors import SlackApiError
from .async_internals import _build_error_response, _is_no_auth_required
from .internals import _to_authorize_result, _is_no_auth_test_call_required, _build_error_text
from ...authorization import AuthorizeResult


class AsyncSingleTeamAuthorization(AsyncAuthorization):
    def __init__(self, base_logger: Optional[Logger] = None):
        """Single-workspace authorization."""
        self.auth_test_result: Optional[AsyncSlackResponse] = None
        self.logger = get_bolt_logger(AsyncSingleTeamAuthorization, base_logger=base_logger)

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
        if _is_no_auth_required(req):
            return await next()

        if _is_no_auth_test_call_required(req):
            req.context.set_authorize_result(
                AuthorizeResult(
                    enterprise_id=req.context.enterprise_id,
                    team_id=req.context.team_id,
                    user_id=req.context.user_id,
                )
            )
            return await next()

        try:
            if self.auth_test_result is None:
                self.auth_test_result = await req.context.client.auth_test()

            if self.auth_test_result:
                req.context.set_authorize_result(
                    _to_authorize_result(
                        auth_test_result=self.auth_test_result,
                        token=req.context.client.token,
                        request_user_id=req.context.user_id,
                    )
                )
                return await next()
            else:
                # Just in case
                self.logger.error("auth.test API call result is unexpectedly None")
                if req.context.response_url is not None:
                    await req.context.respond(_build_error_text())
                    return BoltResponse(status=200, body="")
                return _build_error_response()
        except SlackApiError as e:
            self.logger.error(f"Failed to authorize with the given token ({e})")
            return _build_error_response()
