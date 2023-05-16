import asyncio
import json
from time import time

import pytest
from slack_sdk.signature import SignatureVerifier
from slack_sdk.web.async_client import AsyncWebClient

from slack_bolt import BoltResponse
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.request.async_request import AsyncBoltRequest
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestAsyncListenerMiddleware:
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

    body = {
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

    def build_request(self) -> AsyncBoltRequest:
        timestamp, body = str(int(time())), json.dumps(self.body)
        return AsyncBoltRequest(
            body=body,
            headers={
                "content-type": ["application/json"],
                "x-slack-signature": [
                    self.signature_verifier.generate_signature(
                        body=body,
                        timestamp=timestamp,
                    )
                ],
                "x-slack-request-timestamp": [timestamp],
            },
        )

    @pytest.mark.asyncio
    async def test_return_response(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )

        @app.shortcut(
            constraints="test-shortcut",
            middleware=[listener_middleware_returning_response],
        )
        async def handle(ack):
            await ack()

        response = await app.async_dispatch(self.build_request())
        assert response.status == 200
        assert response.body == "listener middleware"

    @pytest.mark.asyncio
    async def test_next(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )

        @app.shortcut(
            constraints="test-shortcut",
            middleware=[just_next],
        )
        async def handle(ack):
            await ack()

        response = await app.async_dispatch(self.build_request())
        assert response.status == 200


async def listener_middleware_returning_response():
    return BoltResponse(status=200, body="listener middleware")


async def just_next(next):
    await next()
