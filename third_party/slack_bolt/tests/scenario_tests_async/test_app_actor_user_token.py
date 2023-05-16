import asyncio
import datetime
import json
import logging
from time import time
from typing import Optional

import pytest
from slack_sdk.oauth.installation_store import Installation, Bot
from slack_sdk.oauth.installation_store.async_installation_store import (
    AsyncInstallationStore,
)
from slack_sdk.signature import SignatureVerifier
from slack_sdk.web.async_client import AsyncWebClient

from slack_bolt.app.async_app import AsyncApp
from slack_bolt.context.async_context import AsyncBoltContext
from slack_bolt.context.say.async_say import AsyncSay
from slack_bolt.oauth.async_oauth_settings import AsyncOAuthSettings
from slack_bolt.request.async_request import AsyncBoltRequest
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
    assert_auth_test_count_async,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestApp:
    signing_secret = "secret"
    valid_token = "xoxb-valid"
    mock_api_server_base_url = "http://localhost:8888"
    signature_verifier = SignatureVerifier(signing_secret)
    web_client = AsyncWebClient(
        token=valid_token,
        base_url=mock_api_server_base_url,
    )

    @pytest.fixture
    def event_loop(self):
        old_os_env = remove_os_env_temporarily()
        try:
            setup_mock_web_api_server(self)
            loop = asyncio.get_event_loop()
            yield loop
            loop.close()
            cleanup_mock_web_api_server(self)
        finally:
            restore_os_env(old_os_env)

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

    def build_request(self, team_id: str = "T014GJXU940") -> AsyncBoltRequest:
        timestamp, body = str(int(time())), json.dumps(
            {
                "team_id": team_id,
                "enterprise_id": "E013Y3SHLAY",
                "context_team_id": team_id,
                "context_enterprise_id": "E013Y3SHLAY",
                "api_app_id": "A04TEM7H4S0",
                "event": {
                    "type": "message",
                    "files": [],
                    "upload": False,
                    "user": "W013QGS7BPF",
                    "display_as_bot": False,
                    "team": team_id,
                    "channel": "C04T3ACM40K",
                    "subtype": "file_share",
                },
                "type": "event_callback",
                "authorizations": [
                    {
                        "enterprise_id": None,
                        "team_id": "T0G9PQBBK",
                        "user_id": "W23456789",
                        "is_bot": True,
                        "is_enterprise_install": False,
                    }
                ],
                "is_ext_shared_channel": True,
            }
        )
        return AsyncBoltRequest(body=body, headers=self.build_headers(timestamp, body))

    @pytest.mark.asyncio
    async def test_authorize_result(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
            oauth_settings=AsyncOAuthSettings(
                client_id="111.222",
                client_secret="secret",
                installation_store=MemoryInstallationStore(),
                user_token_resolution="actor",
            ),
        )

        @app.event("message")
        async def handle_events(context: AsyncBoltContext, say: AsyncSay):
            assert context.actor_enterprise_id == "E013Y3SHLAY"
            assert context.actor_team_id == "T014GJXU940"
            assert context.actor_user_id == "W013QGS7BPF"

            assert context.authorize_result.bot_id == "BZYBOTHED"
            assert context.authorize_result.bot_user_id == "W23456789"
            assert context.authorize_result.bot_token == "xoxb-valid-2"
            assert context.authorize_result.bot_scopes == ["commands", "chat:write"]
            assert context.authorize_result.user_id == "W99999"
            assert context.authorize_result.user_token == "xoxp-valid-actor-based"
            assert context.authorize_result.user_scopes == ["search:read", "chat:write"]
            await say("What's up?")

        request = self.build_request()
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)
        await asyncio.sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    @pytest.mark.asyncio
    async def test_authorize_result_no_user_token(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
            oauth_settings=AsyncOAuthSettings(
                client_id="111.222",
                client_secret="secret",
                installation_store=MemoryInstallationStore(),
                user_token_resolution="actor",
            ),
        )

        @app.event("message")
        async def handle_events(context: AsyncBoltContext, say: AsyncSay):
            assert context.actor_enterprise_id == "E013Y3SHLAY"
            assert context.actor_team_id == "T11111"
            assert context.actor_user_id == "W013QGS7BPF"

            assert context.authorize_result.bot_id == "BZYBOTHED"
            assert context.authorize_result.bot_user_id == "W23456789"
            assert context.authorize_result.bot_token == "xoxb-valid-2"
            assert context.authorize_result.bot_scopes == ["commands", "chat:write"]
            assert context.authorize_result.user_id is None
            assert context.authorize_result.user_token is None
            assert context.authorize_result.user_scopes is None
            await say("What's up?")

        request = self.build_request(team_id="T11111")
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)
        await asyncio.sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1


class MemoryInstallationStore(AsyncInstallationStore):
    @property
    def logger(self) -> logging.Logger:
        return logging.getLogger(__name__)

    async def async_save(self, installation: Installation):
        pass

    async def async_find_bot(
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

    async def async_find_installation(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        user_id: Optional[str] = None,
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Installation]:
        if team_id == "T0G9PQBBK":
            return Installation(
                app_id="A111",
                enterprise_id="E111",
                team_id="T0G9PQBBK",
                bot_token="xoxb-valid-2",
                bot_id="B",
                bot_user_id="W",
                bot_scopes=["commands", "chat:write"],
                user_id="W11111",
                installed_at=datetime.datetime.now().timestamp(),
            )
        if team_id == "T014GJXU940" and enterprise_id == "E013Y3SHLAY":
            return Installation(
                app_id="A111",
                enterprise_id="E013Y3SHLAY",
                team_id="T014GJXU940",
                user_id="W11111",
                user_token="xoxp-valid-actor-based",
                user_scopes=["search:read", "chat:write"],
                installed_at=datetime.datetime.now().timestamp(),
            )
        return None
