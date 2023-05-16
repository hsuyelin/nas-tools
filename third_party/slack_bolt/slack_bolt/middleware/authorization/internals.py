from typing import Optional, Union

from slack_sdk.web import SlackResponse

from slack_bolt.authorization import AuthorizeResult
from slack_bolt.request.request import BoltRequest
from slack_bolt.response import BoltResponse

#
# NOTE: this source file intentionally avoids having a reference to
# AsyncBoltRequest, AsyncSlackResponse, and whatever Async-prefixed.
#
# The reason why we do so is to enable developers use sync version of Bolt
# without installing aiohttp library (or any others we may use for async things)
#


def _is_url_verification(req: Union[BoltRequest, "AsyncBoltRequest"]) -> bool:  # type: ignore
    return req is not None and req.body is not None and req.body.get("type") == "url_verification"


def _is_ssl_check(req: Union[BoltRequest, "AsyncBoltRequest"]) -> bool:  # type: ignore
    return req is not None and req.body is not None and req.body.get("type") == "ssl_check"


no_auth_test_events = ["app_uninstalled", "tokens_revoked", "team_access_revoked"]


def _is_no_auth_test_events(req: Union[BoltRequest, "AsyncBoltRequest"]) -> bool:  # type: ignore
    return (
        req is not None
        and req.body is not None
        and req.body.get("type") == "event_callback"
        and req.body.get("event", {}).get("type") in no_auth_test_events
    )


def _is_no_auth_required(req: Union[BoltRequest, "AsyncBoltRequest"]) -> bool:  # type: ignore
    return _is_url_verification(req) or _is_ssl_check(req)


def _is_no_auth_test_call_required(req: Union[BoltRequest, "AsyncBoltRequest"]) -> bool:  # type: ignore
    return _is_no_auth_test_events(req)


def _build_error_text() -> str:
    return (
        ":warning: We apologize, but for some unknown reason, your installation with this app is no longer available. "
        "Please reinstall this app into your workspace :bow:"
    )


def _build_error_response() -> BoltResponse:
    # show an ephemeral message to the end-user
    return BoltResponse(
        status=200,
        body=_build_error_text(),
    )


def _is_bot_token(token: Optional[str]) -> bool:
    return token is not None and token.startswith("xoxb-")


def _to_authorize_result(  # type: ignore
    auth_test_result: Union[SlackResponse, "AsyncSlackResponse"],
    token: Optional[str],
    request_user_id: Optional[str],
) -> AuthorizeResult:
    user_id = auth_test_result.get("user_id")
    return AuthorizeResult(
        enterprise_id=auth_test_result.get("enterprise_id"),
        team_id=auth_test_result.get("team_id"),
        bot_id=auth_test_result.get("bot_id"),
        bot_user_id=user_id if _is_bot_token(token) else None,
        bot_token=token if _is_bot_token(token) else None,
        user_id=request_user_id or (user_id if not _is_bot_token(token) else None),
        user_token=token if not _is_bot_token(token) else None,
    )
