import datetime
import json
import logging
from time import time, sleep
from typing import Optional

import pytest
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.oauth import InstallationStore
from slack_sdk.oauth.installation_store import Installation, Bot
from slack_sdk.signature import SignatureVerifier

from slack_bolt import App, BoltRequest, Say, BoltContext
from slack_bolt.authorization import AuthorizeResult
from slack_bolt.authorization.authorize import Authorize
from slack_bolt.error import BoltError
from slack_bolt.oauth.oauth_settings import OAuthSettings
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
    assert_auth_test_count,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class MemoryInstallationStore(InstallationStore):
    @property
    def logger(self) -> logging.Logger:
        return logging.getLogger(__name__)

    def save(self, installation: Installation):
        pass

    def find_bot(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Bot]:
        return Bot(
            app_id="A111",
            enterprise_id="E111",
            team_id="T0G9PQBBK",
            bot_token="xoxb-valid",
            bot_id="B",
            bot_user_id="W",
            bot_scopes=["commands", "chat:write"],
            installed_at=datetime.datetime.now().timestamp(),
        )

    def find_installation(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        user_id: Optional[str] = None,
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Installation]:
        return Installation(
            app_id="A111",
            enterprise_id="E111",
            team_id="T0G9PQBBK",
            bot_token="xoxb-valid-2",
            bot_id="B",
            bot_user_id="W",
            bot_scopes=["commands", "chat:write"],
            user_id="W11111",
            user_token="xoxp-valid",
            user_scopes=["search:read"],
            installed_at=datetime.datetime.now().timestamp(),
        )


class CustomAuthorize(Authorize):
    def __init__(self, installation_store: InstallationStore):
        self.installation_store = installation_store

    def __call__(
        self,
        *,
        context: BoltContext,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        user_id: Optional[str],
    ) -> Optional[AuthorizeResult]:
        bot_token: Optional[str] = None
        user_token: Optional[str] = None
        latest_installation: Optional[Installation] = self.installation_store.find_installation(
            enterprise_id=enterprise_id,
            team_id=team_id,
            is_enterprise_install=context.is_enterprise_install,
        )
        this_user_installation: Optional[Installation] = None
        if latest_installation is not None:
            bot_token = latest_installation.bot_token  # this still can be None
            user_token = latest_installation.user_token  # this still can be None
            if latest_installation.user_id != user_id:
                # First off, remove the user token as the installer is a different user
                user_token = None
                latest_installation.user_token = None
                latest_installation.user_refresh_token = None
                latest_installation.user_token_expires_at = None
                latest_installation.user_scopes = []

                # try to fetch the request user's installation
                # to reflect the user's access token if exists
                this_user_installation = self.installation_store.find_installation(
                    enterprise_id=enterprise_id,
                    team_id=team_id,
                    user_id=user_id,
                    is_enterprise_install=context.is_enterprise_install,
                )
                if this_user_installation is not None:
                    user_token = this_user_installation.user_token
                    if latest_installation.bot_token is None:
                        # If latest_installation has a bot token, we never overwrite the value
                        bot_token = this_user_installation.bot_token
        token: Optional[str] = bot_token or user_token
        if token is None:
            return None
        try:
            auth_test_api_response = context.client.auth_test(token=token)
            authorize_result = AuthorizeResult.from_auth_test_response(
                auth_test_response=auth_test_api_response,
                bot_token=bot_token,
                user_token=user_token,
            )
            return authorize_result
        except SlackApiError:
            return None


class TestApp:
    signing_secret = "secret"
    valid_token = "xoxb-valid"
    mock_api_server_base_url = "http://localhost:8888"
    signature_verifier = SignatureVerifier(signing_secret)
    web_client = WebClient(
        token=valid_token,
        base_url=mock_api_server_base_url,
    )

    def setup_method(self):
        self.old_os_env = remove_os_env_temporarily()
        setup_mock_web_api_server(self)

    def teardown_method(self):
        cleanup_mock_web_api_server(self)
        restore_os_env(self.old_os_env)

    def generate_signature(self, body: str, timestamp: str):
        return self.signature_verifier.generate_signature(
            body=body,
            timestamp=timestamp,
        )

    def build_headers(self, timestamp: str, body: str):
        return {
            "content-type": ["application/json"],
            "x-slack-signature": [self.generate_signature(body, timestamp)],
            "x-slack-request-timestamp": [timestamp],
        }

    app_mention_request_body = {
        "token": "verification_token",
        "team_id": "T111",
        "enterprise_id": "E111",
        "api_app_id": "A111",
        "event": {
            "client_msg_id": "9cbd4c5b-7ddf-4ede-b479-ad21fca66d63",
            "type": "app_mention",
            "text": "<@W111> Hi there!",
            "user": "W222",
            "ts": "1595926230.009600",
            "team": "T111",
            "channel": "C111",
            "event_ts": "1595926230.009600",
        },
        "type": "event_callback",
        "event_id": "Ev111",
        "event_time": 1595926230,
        "authed_users": ["W111"],
    }

    @staticmethod
    def handle_app_mention(body, say: Say, payload, event):
        assert body["event"] == payload
        assert payload == event
        say("What's up?")

    def build_app_mention_request(self):
        timestamp, body = str(int(time())), json.dumps(self.app_mention_request_body)
        return BoltRequest(body=body, headers=self.build_headers(timestamp, body))

    def test_installation_store_only(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
            oauth_settings=OAuthSettings(
                client_id="111.222",
                client_secret="secret",
                scopes=["commands"],
                installation_store=MemoryInstallationStore(),
            ),
        )

        app.event("app_mention")(self.handle_app_mention)
        response = app.dispatch(self.build_app_mention_request())
        assert response.status == 200
        assert_auth_test_count(self, 1)
        sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    def test_installation_store_and_authorize(self):
        installation_store = MemoryInstallationStore()
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
            oauth_settings=OAuthSettings(
                client_id="111.222",
                client_secret="secret",
                scopes=["commands"],
                installation_store=installation_store,
            ),
            authorize=CustomAuthorize(installation_store),
        )

        app.event("app_mention")(self.handle_app_mention)
        response = app.dispatch(self.build_app_mention_request())
        assert response.status == 200
        assert_auth_test_count(self, 1)
        sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    def test_installation_store_and_func_authorize(self):
        installation_store = MemoryInstallationStore()

        def authorize():
            pass

        with pytest.raises(BoltError):
            App(
                client=self.web_client,
                signing_secret=self.signing_secret,
                oauth_settings=OAuthSettings(
                    client_id="111.222",
                    client_secret="secret",
                    scopes=["commands"],
                    installation_store=installation_store,
                ),
                authorize=authorize,
            )
