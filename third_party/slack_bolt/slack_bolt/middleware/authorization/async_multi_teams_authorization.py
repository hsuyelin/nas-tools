from logging import Logger
from typing import Callable, Optional, Awaitable

from slack_sdk.errors import SlackApiError
from slack_bolt.logger import get_bolt_logger
from slack_bolt.request.async_request import AsyncBoltRequest
from slack_bolt.response import BoltResponse
from .async_authorization import AsyncAuthorization
from .async_internals import _build_error_response, _is_no_auth_required
from .internals import _is_no_auth_test_call_required, _build_error_text
from ...authorization import AuthorizeResult
from ...authorization.async_authorize import AsyncAuthorize


class AsyncMultiTeamsAuthorization(AsyncAuthorization):
    authorize: AsyncAuthorize
    user_token_resolution: str

    def __init__(
        self,
        authorize: AsyncAuthorize,
        base_logger: Optional[Logger] = None,
        user_token_resolution: str = "authed_user",
    ):
        """Multi-workspace authorization.

        Args:
            authorize: The function to authorize incoming requests from Slack.
            base_logger: The base logger
            user_token_resolution: "authed_user" or "actor"
        """
        self.authorize = authorize
        self.logger = get_bolt_logger(AsyncMultiTeamsAuthorization, base_logger=base_logger)
        self.user_token_resolution = user_token_resolution

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
            auth_result: Optional[AuthorizeResult] = None
            if self.user_token_resolution == "actor":
                auth_result = await self.authorize(
                    context=req.context,
                    enterprise_id=req.context.enterprise_id,
                    team_id=req.context.team_id,
                    user_id=req.context.user_id,
                    actor_enterprise_id=req.context.actor_enterprise_id,
                    actor_team_id=req.context.actor_team_id,
                    actor_user_id=req.context.actor_user_id,
                )
            else:
                auth_result = await self.authorize(
                    context=req.context,
                    enterprise_id=req.context.enterprise_id,
                    team_id=req.context.team_id,
                    user_id=req.context.user_id,
                )
            if auth_result:
                req.context.set_authorize_result(auth_result)
                token = auth_result.bot_token or auth_result.user_token
                req.context["token"] = token
                # As AsyncApp#_init_context() generates a new AsyncWebClient for this request,
                # it's safe to modify this instance.
                req.context.client.token = token
                return await next()
            else:
                # This situation can arise if:
                # * A developer installed the app from the "Install to Workspace" button in Slack app config page
                # * The InstallationStore failed to save or deleted the installation for this workspace
                self.logger.error(
                    "Although the app should be installed into this workspace, "
                    "the AuthorizeResult (returned value from authorize) for it was not found."
                )
                if req.context.response_url is not None:
                    await req.context.respond(_build_error_text())
                    return BoltResponse(status=200, body="")
                return _build_error_response()

        except SlackApiError as e:
            self.logger.error(f"Failed to authorize with the given token ({e})")
            return _build_error_response()
