import logging
from logging import Logger
from typing import Optional, Callable

from slack_sdk.oauth import RedirectUriPageRenderer, OAuthStateUtils
from slack_sdk.oauth.installation_store import Installation

from slack_bolt.oauth.internals import CallbackResponseBuilder
from slack_bolt.request import BoltRequest
from slack_bolt.response import BoltResponse


class SuccessArgs:
    def __init__(  # type: ignore
        self,
        *,
        request: BoltRequest,
        installation: Installation,
        settings: "OAuthSettings",
        default: "CallbackOptions",
    ):
        """The arguments for a success function.

        Args:
            request: The request.
            installation: The installation data.
            settings: The settings for Slack OAuth flow.
            default: The default `CallbackOptions`
        """
        self.request = request
        self.installation = installation
        self.settings = settings
        self.default = default


class FailureArgs:
    def __init__(  # type: ignore
        self,
        *,
        request: BoltRequest,
        reason: str,
        error: Optional[Exception] = None,
        suggested_status_code: int,
        settings: "OAuthSettings",
        default: "CallbackOptions",
    ):
        """The arguments for a failure function.

        Args:
            request: The request.
            reason: The response.
            error: An exception if exists.
            suggested_status_code: The recommended HTTP status code for the failure.
            settings: The settings for Slack OAuth flow.
            default: The default `CallbackOptions`.
        """
        self.request = request
        self.reason = reason
        self.error = error
        self.suggested_status_code = suggested_status_code
        self.settings = settings
        self.default = default


class CallbackOptions:
    success: Callable[[SuccessArgs], BoltResponse]
    failure: Callable[[FailureArgs], BoltResponse]

    def __init__(
        self,
        success: Callable[[SuccessArgs], BoltResponse],
        failure: Callable[[FailureArgs], BoltResponse],
    ):
        """The configurations for OAuth flow.

        Args:
            success: A handler for successful installation.
            failure: A handler for any types of installation failures.
        """
        self.success = success
        self.failure = failure


class DefaultCallbackOptions(CallbackOptions):
    success: Callable[[SuccessArgs], BoltResponse]
    failure: Callable[[FailureArgs], BoltResponse]

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
        self.success = self._success_handler
        self.failure = self._failure_handler

    # --------------------------
    # Internal methods
    # --------------------------

    def _success_handler(self, args: SuccessArgs) -> BoltResponse:
        return self._response_builder._build_callback_success_response(
            request=args.request,
            installation=args.installation,
        )

    def _failure_handler(self, args: FailureArgs) -> BoltResponse:
        return self._response_builder._build_callback_failure_response(
            request=args.request,
            reason=args.reason,
            status=args.suggested_status_code,
        )
