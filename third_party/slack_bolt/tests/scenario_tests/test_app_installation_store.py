import datetime
import json
import logging
from time import time, sleep
from typing import Optional

from slack_sdk import WebClient
from slack_sdk.oauth import InstallationStore
from slack_sdk.oauth.installation_store import Installation, Bot
from slack_sdk.signature import SignatureVerifier

from slack_bolt import App, BoltRequest, Say, BoltContext
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

    def build_app_mention_request(self):
        timestamp, body = str(int(time())), json.dumps(
            {
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
        )
        return BoltRequest(body=body, headers=self.build_headers(timestamp, body))

    def test_authorize_result(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
            oauth_settings=OAuthSettings(
                client_id="111.222",
                client_secret="secret",
                scopes=["commands"],
                user_scopes=["search:read"],
                installation_store=MemoryInstallationStore(),
            ),
        )

        @app.event("app_mention")
        def handle_app_mention(context: BoltContext, say: Say):
            assert context.authorize_result.bot_id == "BZYBOTHED"
            assert context.authorize_result.bot_user_id == "W23456789"
            assert context.authorize_result.bot_token == "xoxb-valid-2"
            assert context.authorize_result.bot_scopes == ["commands", "chat:write"]
            assert context.authorize_result.user_id == "W99999"
            assert context.authorize_result.user_token == "xoxp-valid"
            assert context.authorize_result.user_scopes == ["search:read"]
            say("What's up?")

        response = app.dispatch(self.build_app_mention_request())
        assert response.status == 200
        assert_auth_test_count(self, 1)
        sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1
