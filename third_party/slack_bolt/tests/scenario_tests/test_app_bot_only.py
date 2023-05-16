import datetime
import json
import logging
from time import time, sleep
from typing import Optional

from slack_sdk import WebClient
from slack_sdk.oauth import InstallationStore
from slack_sdk.oauth.installation_store import Installation, Bot
from slack_sdk.oauth.state_store import FileOAuthStateStore
from slack_sdk.signature import SignatureVerifier

from slack_bolt import App, BoltRequest, Say
from slack_bolt.oauth import OAuthFlow
from slack_bolt.oauth.oauth_settings import OAuthSettings
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
    assert_auth_test_count,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class LegacyMemoryInstallationStore(InstallationStore):
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


class MemoryInstallationStore(LegacyMemoryInstallationStore):
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


class BotOnlyMemoryInstallationStore(LegacyMemoryInstallationStore):
    def find_installation(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        user_id: Optional[str] = None,
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Installation]:
        raise ValueError


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

    oauth_settings_bot_only = OAuthSettings(
        client_id="111.222",
        client_secret="valid",
        installation_store=BotOnlyMemoryInstallationStore(),
        installation_store_bot_only=True,
        state_store=FileOAuthStateStore(expiration_seconds=120),
    )

    oauth_settings = OAuthSettings(
        client_id="111.222",
        client_secret="valid",
        installation_store=BotOnlyMemoryInstallationStore(),
        installation_store_bot_only=False,
        state_store=FileOAuthStateStore(expiration_seconds=120),
    )

    def build_app_mention_request(self):
        timestamp, body = str(int(time())), json.dumps(self.app_mention_request_body)
        return BoltRequest(body=body, headers=self.build_headers(timestamp, body))

    def test_installation_store_bot_only_default(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
            installation_store=MemoryInstallationStore(),
        )

        app.event("app_mention")(self.handle_app_mention)
        response = app.dispatch(self.build_app_mention_request())
        assert response.status == 200
        assert_auth_test_count(self, 1)
        sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    def test_installation_store_bot_only_false(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
            installation_store=MemoryInstallationStore(),
            # the default is False
            installation_store_bot_only=False,
        )

        app.event("app_mention")(self.handle_app_mention)
        response = app.dispatch(self.build_app_mention_request())
        assert response.status == 200
        assert_auth_test_count(self, 1)
        sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    def test_installation_store_bot_only(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
            installation_store=BotOnlyMemoryInstallationStore(),
            installation_store_bot_only=True,
        )

        app.event("app_mention")(self.handle_app_mention)
        response = app.dispatch(self.build_app_mention_request())
        assert response.status == 200
        assert_auth_test_count(self, 1)
        sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    def test_installation_store_bot_only_oauth_settings(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
            oauth_settings=self.oauth_settings_bot_only,
        )

        app.event("app_mention")(self.handle_app_mention)
        response = app.dispatch(self.build_app_mention_request())
        assert response.status == 200
        assert_auth_test_count(self, 1)
        sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    def test_installation_store_bot_only_oauth_settings_conflicts(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
            installation_store_bot_only=True,
            oauth_settings=self.oauth_settings,
        )

        app.event("app_mention")(self.handle_app_mention)
        response = app.dispatch(self.build_app_mention_request())
        assert response.status == 200
        assert_auth_test_count(self, 1)
        sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    def test_installation_store_bot_only_oauth_flow(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
            oauth_flow=OAuthFlow(settings=self.oauth_settings_bot_only),
        )

        app.event("app_mention")(self.handle_app_mention)
        response = app.dispatch(self.build_app_mention_request())
        assert response.status == 200
        assert_auth_test_count(self, 1)
        sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    def test_installation_store_bot_only_oauth_flow_conflicts(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
            installation_store_bot_only=True,
            oauth_flow=OAuthFlow(settings=self.oauth_settings),
        )

        app.event("app_mention")(self.handle_app_mention)
        response = app.dispatch(self.build_app_mention_request())
        assert response.status == 200
        assert_auth_test_count(self, 1)
        sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1
