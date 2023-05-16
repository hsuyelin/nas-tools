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


class TestAsyncViewClosed:
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
        app.view({"type": "view_closed", "callback_id": "view-id"})(simple_listener)

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
        app.view_closed("view-id")(simple_listener)

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
        app.view({"type": "view_closed", "callback_id": "view-id"})(simple_listener)

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

        app.view("view-idddd")(simple_listener)
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

        app.view({"type": "view_closed", "callback_id": "view-idddd"})(simple_listener)
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

        app.view_closed("view-idddd")(simple_listener)
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)


body = {
    "type": "view_closed",
    "team": {
        "id": "T111",
        "domain": "workspace-domain",
        "enterprise_id": "E111",
        "enterprise_name": "Sandbox Org",
    },
    "user": {
        "id": "W111",
        "username": "primary-owner",
        "name": "primary-owner",
        "team_id": "T111",
    },
    "api_app_id": "A111",
    "token": "verification_token",
    "view": {
        "id": "V111",
        "team_id": "T111",
        "type": "modal",
        "blocks": [
            {
                "type": "input",
                "block_id": "hspI",
                "label": {
                    "type": "plain_text",
                    "text": "Label",
                },
                "optional": False,
                "element": {"type": "plain_text_input", "action_id": "maBWU"},
            }
        ],
        "private_metadata": "This is for you!",
        "callback_id": "view-id",
        "state": {"values": {}},
        "hash": "1596530361.3wRYuk3R",
        "title": {
            "type": "plain_text",
            "text": "My App",
        },
        "clear_on_close": False,
        "notify_on_close": False,
        "close": {
            "type": "plain_text",
            "text": "Cancel",
        },
        "submit": {
            "type": "plain_text",
            "text": "Submit",
        },
        "previous_view_id": None,
        "root_view_id": "V111",
        "app_id": "A111",
        "external_id": "",
        "app_installed_team_id": "T111",
        "bot_id": "B111",
    },
    "response_urls": [],
}

raw_body = f"payload={quote(json.dumps(body))}"


async def simple_listener(ack, body, payload, view):
    assert body["view"] == view
    assert payload == view
    assert view["private_metadata"] == "This is for you!"
    await ack()
