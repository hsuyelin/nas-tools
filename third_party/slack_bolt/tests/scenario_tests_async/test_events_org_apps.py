import asyncio
import json
from time import time
from typing import Optional

import pytest
from slack_sdk.oauth.installation_store import Installation
from slack_sdk.oauth.installation_store.async_installation_store import (
    AsyncInstallationStore,
)
from slack_sdk.signature import SignatureVerifier
from slack_sdk.web.async_client import AsyncWebClient

from slack_bolt.app.async_app import AsyncApp
from slack_bolt.request.async_request import AsyncBoltRequest
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
    assert_auth_test_count_async,
)
from tests.utils import remove_os_env_temporarily, restore_os_env

valid_token = "xoxb-valid"


class OrgAppInstallationStore(AsyncInstallationStore):
    async def async_find_installation(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        user_id: Optional[str] = None,
        is_enterprise_install: Optional[bool] = False
    ) -> Optional[Installation]:
        assert enterprise_id == "E111"
        assert team_id is None
        return Installation(
            enterprise_id="E111",
            team_id=None,
            user_id=user_id,
            bot_token=valid_token,
            bot_id="B111",
        )


class Result:
    def __init__(self):
        self.called = False


class TestAsyncOrgApps:
    signing_secret = "secret"
    valid_token = "xoxb-valid"
    mock_api_server_base_url = "http://localhost:8888"
    signature_verifier = SignatureVerifier(signing_secret)
    web_client = AsyncWebClient(token=None, base_url=mock_api_server_base_url)

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

    @pytest.mark.asyncio
    async def test_team_access_granted(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
            installation_store=OrgAppInstallationStore(),
        )

        event_payload = {
            "token": "verification-token",
            "enterprise_id": "E111",
            "api_app_id": "A111",
            "event": {
                "type": "team_access_granted",
                "team_ids": ["T111", "T222"],
                "event_ts": "111.222",
            },
            "type": "event_callback",
            "event_id": "Ev111",
            "event_time": 1606805974,
        }

        result = Result()

        @app.event("team_access_granted")
        async def handle_app_mention(body):
            assert body == event_payload
            result.called = True

        timestamp, body = str(int(time())), json.dumps(event_payload)
        request: AsyncBoltRequest = AsyncBoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = await app.async_dispatch(request)
        assert response.status == 200
        # auth.test API call must be skipped
        await assert_auth_test_count_async(self, 1)
        await asyncio.sleep(1)  # wait a bit after auto ack()
        assert result.called is True

    @pytest.mark.asyncio
    async def test_team_access_revoked(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
            installation_store=OrgAppInstallationStore(),
        )

        event_payload = {
            "token": "verification-token",
            "enterprise_id": "E111",
            "api_app_id": "A111",
            "event": {
                "type": "team_access_revoked",
                "team_ids": ["T111", "T222"],
                "event_ts": "1606805732.987656",
            },
            "type": "event_callback",
            "event_id": "Ev111",
            "event_time": 1606805732,
        }

        result = Result()

        @app.event("team_access_revoked")
        async def handle_app_mention(body):
            assert body == event_payload
            result.called = True

        timestamp, body = str(int(time())), json.dumps(event_payload)
        request: AsyncBoltRequest = AsyncBoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = await app.async_dispatch(request)
        assert response.status == 200
        # auth.test API call must be skipped
        assert self.mock_received_requests.get("/auth.test") is None
        await asyncio.sleep(1)  # wait a bit after auto ack()
        assert result.called is True

    @pytest.mark.asyncio
    async def test_app_home_opened(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
            installation_store=OrgAppInstallationStore(),
        )

        event_payload = {
            "token": "verification-token",
            "team_id": "T111",
            "enterprise_id": "E111",
            "api_app_id": "A111",
            "event": {
                "type": "app_home_opened",
                "user": "W111",
                "channel": "D111",
                "tab": "messages",
                "event_ts": "1606810927.510671",
            },
            "type": "event_callback",
            "event_id": "Ev111",
            "event_time": 1606810927,
            "authorizations": [
                {
                    "enterprise_id": "E111",
                    "team_id": None,
                    "user_id": "W111",
                    "is_bot": True,
                    "is_enterprise_install": True,
                }
            ],
            "is_ext_shared_channel": False,
        }

        result = Result()

        @app.event("app_home_opened")
        async def handle_app_mention(body):
            assert body == event_payload
            result.called = True

        timestamp, body = str(int(time())), json.dumps(event_payload)
        request: AsyncBoltRequest = AsyncBoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = await app.async_dispatch(request)
        assert response.status == 200
        # auth.test API call must be skipped
        await assert_auth_test_count_async(self, 1)
        await asyncio.sleep(1)  # wait a bit after auto ack()
        assert result.called is True

    @pytest.mark.asyncio
    async def test_message(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
            installation_store=OrgAppInstallationStore(),
        )

        event_payload = {
            "token": "verification-token",
            "team_id": "T111",
            "enterprise_id": "E111",
            "api_app_id": "A111",
            "event": {
                "client_msg_id": "0186b75a-2ad4-4f36-8ccc-18608b0ac5d1",
                "type": "message",
                "text": "<@W222>",
                "user": "W111",
                "ts": "1606810819.000800",
                "team": "T111",
                "channel": "C111",
                "event_ts": "1606810819.000800",
                "channel_type": "channel",
            },
            "type": "event_callback",
            "event_id": "Ev111",
            "event_time": 1606810819,
            "authed_users": [],
            "authorizations": [
                {
                    "enterprise_id": "E111",
                    "team_id": None,
                    "user_id": "W222",
                    "is_bot": True,
                    "is_enterprise_install": True,
                }
            ],
            "is_ext_shared_channel": False,
            "event_context": "1-message-T111-C111",
        }

        result = Result()

        @app.event("message")
        async def handle_app_mention(body):
            assert body == event_payload
            result.called = True

        timestamp, body = str(int(time())), json.dumps(event_payload)
        request: AsyncBoltRequest = AsyncBoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = await app.async_dispatch(request)
        assert response.status == 200
        # auth.test API call must be skipped
        await assert_auth_test_count_async(self, 1)
        await asyncio.sleep(1)  # wait a bit after auto ack()
        assert result.called is True
