import asyncio
import json
from time import time
from urllib.parse import quote

import pytest
from slack_sdk.signature import SignatureVerifier
from slack_sdk.web.async_client import AsyncWebClient

from slack_bolt.app.async_app import AsyncApp
from slack_bolt.context.async_context import AsyncBoltContext
from slack_bolt.request.async_request import AsyncBoltRequest
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
    assert_auth_test_count_async,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestAsyncBlockActions:
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
            "content-type": ["application/x-www-form-urlencoded"],
            "x-slack-signature": [self.generate_signature(body, timestamp)],
            "x-slack-request-timestamp": [timestamp],
        }

    def build_valid_request(self) -> AsyncBoltRequest:
        timestamp = str(int(time()))
        return AsyncBoltRequest(body=raw_body, headers=self.build_headers(timestamp, raw_body))

    @pytest.mark.asyncio
    async def test_mock_server_is_running(self):
        resp = await self.web_client.api_test()
        assert resp != None

    @pytest.mark.asyncio
    async def test_success(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.action("a")(simple_listener)

        request = self.build_valid_request()
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_success_2(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.block_action("a")(simple_listener)

        request = self.build_valid_request()
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_default_type(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.action({"action_id": "a", "block_id": "b"})(simple_listener)

        request = self.build_valid_request()
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_default_type_no_block_id(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.action({"action_id": "a"})(simple_listener)

        request = self.build_valid_request()
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_default_type_unmatched_block_id(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.action({"action_id": "a", "block_id": "bbb"})(simple_listener)

        request = self.build_valid_request()
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_process_before_response(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
            process_before_response=True,
        )
        app.action("a")(simple_listener)

        request = self.build_valid_request()
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_process_before_response_2(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
            process_before_response=True,
        )
        app.block_action("a")(simple_listener)

        request = self.build_valid_request()
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_failure(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        request = self.build_valid_request()
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

        app.action("aaa")(simple_listener)
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_failure_2(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        request = self.build_valid_request()
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

        app.block_action("aaa")(simple_listener)
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)


body = {
    "type": "block_actions",
    "user": {
        "id": "W111",
        "username": "primary-owner",
        "name": "primary-owner",
        "team_id": "T111",
    },
    "api_app_id": "A111",
    "token": "verification_token",
    "container": {
        "type": "message",
        "message_ts": "111.222",
        "channel_id": "C111",
        "is_ephemeral": True,
    },
    "trigger_id": "111.222.valid",
    "team": {
        "id": "T111",
        "domain": "workspace-domain",
        "enterprise_id": "E111",
        "enterprise_name": "Sandbox Org",
    },
    "channel": {"id": "C111", "name": "test-channel"},
    "response_url": "https://hooks.slack.com/actions/T111/111/random-value",
    "actions": [
        {
            "action_id": "a",
            "block_id": "b",
            "text": {"type": "plain_text", "text": "Button", "emoji": True},
            "value": "click_me_123",
            "type": "button",
            "action_ts": "1596530385.194939",
        }
    ],
}

raw_body = f"payload={quote(json.dumps(body))}"


async def simple_listener(ack, body, payload, action, context: AsyncBoltContext):
    assert body["trigger_id"] == "111.222.valid"
    assert body["actions"][0] == payload
    assert payload == action
    assert action["action_id"] == "a"
    assert context.bot_id == "BZYBOTHED"
    assert context.bot_user_id == "W23456789"
    assert context.bot_token == "xoxb-valid"
    assert context.token == "xoxb-valid"
    assert context.user_id == "W111"
    assert context.user_token is None
    await ack()
