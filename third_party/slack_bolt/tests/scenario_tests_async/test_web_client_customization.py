import asyncio
import json
import os
from time import time
from urllib.parse import quote

import pytest
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.http_retry.builtin_async_handlers import AsyncConnectionErrorRetryHandler, AsyncRateLimitErrorRetryHandler
from slack_sdk.signature import SignatureVerifier

from slack_bolt.request.async_request import AsyncBoltRequest
from slack_bolt.async_app import AsyncApp
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
    assert_auth_test_count_async,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestWebClientCustomization:
    valid_token = "xoxb-valid"
    signing_secret = "secret"
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
    async def test_web_client_customization(self):
        if os.environ.get("BOLT_PYTHON_CODECOV_RUNNING") == "1":
            # Traceback (most recent call last):
            #   File "/opt/hostedtoolcache/Python/3.11.2/x64/lib/python3.11/site-packages/slack_sdk-3.20.0-py3.11.egg/slack_sdk/web/async_internal_utils.py", line 151, in _request_with_session
            #     if await handler.can_retry_async(
            #              ^^^^^^^^^^^^^^^^^^^^^^^^
            # TypeError: AsyncRetryHandler.can_retry_async() missing 1 required positional argument: 'self'
            return

        self.web_client.retry_handlers = [
            AsyncConnectionErrorRetryHandler(),
            AsyncRateLimitErrorRetryHandler(),
        ]
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )

        @app.action("a")
        async def listener(ack, client):
            assert len(client.retry_handlers) == 2
            await ack()

        request = self.build_valid_request()
        response = await app.async_dispatch(request)
        assert response.status == 200
        assert response.body == ""
        await assert_auth_test_count_async(self, 1)


block_actions_body = {
    "type": "block_actions",
    "user": {
        "id": "W99999",
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

raw_body = f"payload={quote(json.dumps(block_actions_body))}"
