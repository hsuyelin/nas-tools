import asyncio
import json
from time import time
from urllib.parse import quote

import pytest
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


class TestAsyncShortcut:
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

    def build_valid_request(self, body) -> AsyncBoltRequest:
        timestamp = str(int(time()))
        return AsyncBoltRequest(body=body, headers=self.build_headers(timestamp, body))

    @pytest.mark.asyncio
    async def test_mock_server_is_running(self):
        resp = await self.web_client.api_test()
        assert resp != None

    # NOTE: This is a compatible behavior with Bolt for JS
    @pytest.mark.asyncio
    async def test_success_both_global_and_message(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.shortcut("test-shortcut")(simple_listener)

        request = self.build_valid_request(global_shortcut_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)

        request = self.build_valid_request(message_shortcut_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_success_global(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.shortcut("test-shortcut")(simple_listener)

        request = self.build_valid_request(global_shortcut_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_success_global_2(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.global_shortcut("test-shortcut")(simple_listener)

        request = self.build_valid_request(global_shortcut_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)

        request = self.build_valid_request(message_shortcut_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_success_message(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.shortcut({"type": "message_action", "callback_id": "test-shortcut"})(simple_listener)

        request = self.build_valid_request(message_shortcut_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)

        request = self.build_valid_request(global_shortcut_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_success_message_2(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.message_shortcut("test-shortcut")(simple_listener)

        request = self.build_valid_request(message_shortcut_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)

        request = self.build_valid_request(global_shortcut_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_process_before_response_global(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
            process_before_response=True,
        )
        app.shortcut("test-shortcut")(simple_listener)

        request = self.build_valid_request(global_shortcut_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_failure(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        request = self.build_valid_request(global_shortcut_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

        app.shortcut("another-one")(simple_listener)
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_failure_2(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        request = self.build_valid_request(global_shortcut_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

        app.global_shortcut("another-one")(simple_listener)
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

        request = self.build_valid_request(message_shortcut_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)


global_shortcut_body = {
    "type": "shortcut",
    "token": "verification_token",
    "action_ts": "111.111",
    "team": {
        "id": "T111",
        "domain": "workspace-domain",
        "enterprise_id": "E111",
        "enterprise_name": "Org Name",
    },
    "user": {"id": "W111", "username": "primary-owner", "team_id": "T111"},
    "callback_id": "test-shortcut",
    "trigger_id": "111.111.xxxxxx",
}

message_shortcut_body = {
    "type": "message_action",
    "token": "verification_token",
    "action_ts": "1583637157.207593",
    "team": {
        "id": "T111",
        "domain": "test-test",
        "enterprise_id": "E111",
        "enterprise_name": "Org Name",
    },
    "user": {"id": "W111", "name": "test-test"},
    "channel": {"id": "C111", "name": "dev"},
    "callback_id": "test-shortcut",
    "trigger_id": "111.222.xxx",
    "message_ts": "1583636382.000300",
    "message": {
        "client_msg_id": "zzzz-111-222-xxx-yyy",
        "type": "message",
        "text": "<@W222> test",
        "user": "W111",
        "ts": "1583636382.000300",
        "team": "T111",
        "blocks": [
            {
                "type": "rich_text",
                "block_id": "d7eJ",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {"type": "user", "user_id": "U222"},
                            {"type": "text", "text": " test"},
                        ],
                    }
                ],
            }
        ],
    },
    "response_url": "https://hooks.slack.com/app/T111/111/xxx",
}

global_shortcut_raw_body = f"payload={quote(json.dumps(global_shortcut_body))}"
message_shortcut_raw_body = f"payload={quote(json.dumps(message_shortcut_body))}"


async def simple_listener(ack, body, payload, shortcut):
    assert body == shortcut
    assert payload == shortcut
    await ack()
