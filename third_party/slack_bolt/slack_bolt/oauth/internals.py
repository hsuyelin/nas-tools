from logging import Logger
from typing import Optional
from typing import Union

from slack_sdk.oauth import InstallationStore
from slack_sdk.oauth import OAuthStateUtils, RedirectUriPageRenderer
from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.oauth.installation_store import Installation

from slack_bolt.request import BoltRequest
from slack_bolt.response import BoltResponse
from ..logger.messages import warning_installation_store_conflicts


class CallbackResponseBuilder:
    def __init__(
        self,
        *,
        logger: Logger,
        state_utils: OAuthStateUtils,
        redirect_uri_page_renderer: RedirectUriPageRenderer,
    ):
        self._logger = logger
        self._state_utils = state_utils
        self._redirect_uri_page_renderer = redirect_uri_page_renderer

    def _build_callback_success_response(  # type: ignore
        self,
        request: Union[BoltRequest, "AsyncBoltRequest"],
        installation: Installation,
    ) -> BoltResponse:
        debug_message = f"Handling an OAuth callback success (request: {request.query})"
        self._logger.debug(debug_message)

        html = self._redirect_uri_page_renderer.render_success_page(
            app_id=installation.app_id,
            team_id=installation.team_id,
            is_enterprise_install=installation.is_enterprise_install,
            enterprise_url=installation.enterprise_url,
        )
        return BoltResponse(
            status=200,
            headers={
                "Content-Type": "text/html; charset=utf-8",
                "Set-Cookie": self._state_utils.build_set_cookie_for_deletion(),
            },
            body=html,
        )

    def _build_callback_failure_response(  # type: ignore
        self,
        request: Union[BoltRequest, "AsyncBoltRequest"],
        reason: str,
        status: int = 500,
        error: Optional[Exception] = None,
    ) -> BoltResponse:
        debug_message = "Handling an OAuth callback failure " f"(reason: {reason}, error: {error}, request: {request.query})"
        self._logger.debug(debug_message)

        # Adding a bit more details to the error code to help installers understand what's happening.
        # This modification in the HTML page works only when developers use this built-in failure handler.
        detailed_error = build_detailed_error(reason)
        html = self._redirect_uri_page_renderer.render_failure_page(detailed_error)
        return BoltResponse(
            status=status,
            headers={
                "Content-Type": "text/html; charset=utf-8",
                "Set-Cookie": self._state_utils.build_set_cookie_for_deletion(),
            },
            body=html,
        )


def _build_default_install_page_html(url: str) -> str:
    return f"""<html>
<head>
<link rel="icon" href="data:,">
<style>
body {{
  padding: 10px 15px;
  font-family: verdana;
  text-align: center;
}}
</style>
</head>
<body>
<h2>Slack App Installation</h2>
<p><a href="{url}"><img alt=""Add to Slack"" height="40" width="139" src="https://platform.slack-edge.com/img/add_to_slack.png" srcset="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x" /></a></p>
</body>
</html>
"""  # noqa: E501


# key: client_id, value: InstallationStore
default_installation_stores = {}


def get_or_create_default_installation_store(client_id: str) -> InstallationStore:
    store = default_installation_stores.get(client_id)
    if store is None:
        store = FileInstallationStore(client_id=client_id)
        default_installation_stores[client_id] = store
    return store


def select_consistent_installation_store(
    client_id: str,
    app_store: Optional[InstallationStore],
    oauth_flow_store: Optional[InstallationStore],
    logger: Logger,
) -> Optional[InstallationStore]:
    default = get_or_create_default_installation_store(client_id)
    if app_store is not None:
        if oauth_flow_store is not None:
            if oauth_flow_store is default:
                # only app_store is intentionally set in this case
                return app_store

            # if both are intentionally set, prioritize app_store
            if oauth_flow_store is not app_store:
                logger.warning(warning_installation_store_conflicts())
            return oauth_flow_store
        else:
            # only app_store is available
            return app_store
    else:
        # only oauth_flow_store is available
        return oauth_flow_store


def build_detailed_error(reason: str) -> str:
    if reason == "invalid_browser":
        return (
            f"{reason}: This can occur due to page reload, "
            "not beginning the OAuth flow from the valid starting URL, or "
            "the /slack/install URL not using https://"
        )
    elif reason == "invalid_state":
        return f"{reason}: The state parameter is no longer valid."
    elif reason == "missing_code":
        return f"{reason}: The code parameter is missing in this redirection."
    elif reason == "storage_error":
        return f"{reason}: The app's server encountered an issue. Contact the app developer."
    else:
        return f"{reason}: This error code is returned from Slack. Refer to the documents for details."
