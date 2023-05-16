import logging
from logging import Logger
from typing import Optional, Callable, Awaitable

from slack_sdk.oauth import RedirectUriPageRenderer, OAuthStateUtils
from slack_sdk.oauth.installation_store import Installation
from slack_bolt.oauth.internals import CallbackResponseBuilder

from slack_bolt.request.async_request import AsyncBoltRequest
from slack_bolt.response import BoltResponse


class AsyncSuccessArgs:
    def __init__(  # type: ignore
        self,
        *,
        request: AsyncBoltRequest,
        installation: Installation,
        settings: "AsyncOAuthSettings",
        default: "AsyncCallbackOptions",
    ):
        """The arguments for a success function.

        Args:
            request: The request.
            installation: The installation data.
            settings: The settings for Slack OAuth flow.
            default: The default `AsyncCallbackOptions`.
        """
        self.request = request
        self.installation = installation
        self.settings = settings
        self.default = default


class AsyncFailureArgs:
    def __init__(  # type: ignore
        self,
        *,
        request: AsyncBoltRequest,
        reason: str,
        error: Optional[Exception] = None,
        suggested_status_code: int,
        settings: "AsyncOAuthSettings",
        default: "AsyncCallbackOptions",
    ):
        """The arguments for a failure function.

        Args:
            request: The request.
            reason: The response.
            error: An exception if exists.
            suggested_status_code: The recommended HTTP status code for the failure.
            settings: The settings for Slack OAuth flow.
            default: The default `AsyncCallbackOptions`.
        """
        self.request = request
        self.reason = reason
        self.error = error
        self.suggested_status_code = suggested_status_code
        self.settings = settings
        self.default = default


class AsyncCallbackOptions:
    success: Callable[[AsyncSuccessArgs], Awaitable[BoltResponse]]
    failure: Callable[[AsyncFailureArgs], Awaitable[BoltResponse]]

    def __init__(
        self,
        success: Callable[[AsyncSuccessArgs], Awaitable[BoltResponse]],
        failure: Callable[[AsyncFailureArgs], Awaitable[BoltResponse]],
    ):
        self.success = success
        self.failure = failure


class DefaultAsyncCallbackOptions(AsyncCallbackOptions):
    success: Callable[[AsyncSuccessArgs], Awaitable[BoltResponse]]
    failure: Callable[[AsyncFailureArgs], Awaitable[BoltResponse]]

    def __init__(
        self,
        *,
        logger: Logger,
        state_utils: OAuthStateUtils,
        redirect_uri_page_renderer: RedirectUriPageRenderer,
    ):
        self._response_builder = CallbackResponseBuilder(
            logger=logger or logging.getLogger(__name__),
            state_utils=state_utils,
            redirect_uri_page_renderer=redirect_uri_page_renderer,
        )
        # Note that pytype 2021.4.26 misunderstands these assignments.
        # Thus, we put "type: ignore" for the following two lines
        self.success = self._success_handler  # type: ignore
        self.failure = self._failure_handler  # type: ignore

    # --------------------------
    # Internal methods
    # --------------------------

    async def _success_handler(self, args: AsyncSuccessArgs) -> BoltResponse:
        return self._response_builder._build_callback_success_response(
            request=args.request,
            installation=args.installation,
        )

    async def _failure_handler(self, args: AsyncFailureArgs) -> BoltResponse:
        return self._response_builder._build_callback_failure_response(
            request=args.request,
            reason=args.reason,
            status=args.suggested_status_code,
        )
