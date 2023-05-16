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


class TestAsyncAttachmentActions:
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
    async def test_success_without_type(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.action("pick_channel_for_fun")(simple_listener)

        request = self.build_valid_request()
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_success(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.action(
            {
                "callback_id": "pick_channel_for_fun",
                "type": "interactive_message",
            }
        )(simple_listener)

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
        app.attachment_action("pick_channel_for_fun")(simple_listener)

        request = self.build_valid_request()
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_process_before_response(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
            process_before_response=True,
        )
        app.action(
            {
                "callback_id": "pick_channel_for_fun",
                "type": "interactive_message",
            }
        )(simple_listener)

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
        app.attachment_action("pick_channel_for_fun")(simple_listener)

        request = self.build_valid_request()
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_failure_without_type(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        request = self.build_valid_request()
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

        app.action("unknown")(simple_listener)
        response = await app.async_dispatch(request)
        assert response.status == 404
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

        app.action(
            {
                "callback_id": "unknown",
                "type": "interactive_message",
            }
        )(simple_listener)
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

        app.attachment_action("unknown")(simple_listener)
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)


# https://api.slack.com/legacy/interactive-messages
body = {
    "type": "interactive_message",
    "actions": [
        {
            "name": "channel_list",
            "type": "select",
            "selected_options": [{"value": "C111"}],
        }
    ],
    "callback_id": "pick_channel_for_fun",
    "team": {"id": "T111", "domain": "hooli-hq"},
    "channel": {"id": "C222", "name": "triage-random"},
    "user": {"id": "U111", "name": "gbelson"},
    "action_ts": "1520966872.245369",
    "message_ts": "1520965348.000538",
    "attachment_id": "1",
    "token": "verification_token",
    "is_app_unfurl": True,
    "original_message": {
        "text": "",
        "username": "Belson Bot",
        "bot_id": "B111",
        "attachments": [
            {
                "callback_id": "pick_channel_for_fun",
                "text": "Choose a channel",
                "id": 1,
                "color": "2b72cb",
                "actions": [
                    {
                        "id": "1",
                        "name": "channel_list",
                        "text": "Public channels",
                        "type": "select",
                        "data_source": "channels",
                    }
                ],
                "fallback": "Choose a channel",
            }
        ],
        "type": "message",
        "subtype": "bot_message",
        "ts": "1520965348.000538",
    },
    "response_url": "https://hooks.slack.com/actions/T111/111/xxxx",
    "trigger_id": "111.222.valid",
}

raw_body = f"payload={quote(json.dumps(body))}"


async def simple_listener(ack, body, payload, action):
    assert body != payload
    assert payload == action
    assert body["trigger_id"] == "111.222.valid"
    await ack()
