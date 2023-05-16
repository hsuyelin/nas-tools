import asyncio
import json
from time import time
from typing import Optional

import pytest
from slack_sdk.oauth.installation_store.async_installation_store import (
    AsyncInstallationStore,
)
from slack_sdk.signature import SignatureVerifier
from slack_sdk.web.async_client import AsyncWebClient

from slack_bolt.app.async_app import AsyncApp
from slack_bolt.error import BoltError
from slack_bolt.request.async_request import AsyncBoltRequest
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
    assert_auth_test_count_async,
)
from tests.utils import remove_os_env_temporarily, restore_os_env

valid_token = "xoxb-valid"


class MyInstallationStore(AsyncInstallationStore):
    def __init__(self):
        self.delete_bot_called = False
        self.delete_installation_called = False
        self.delete_all_called = False

    async def async_delete_bot(self, *, enterprise_id: Optional[str], team_id: Optional[str]) -> None:
        self.delete_bot_called = True

    async def async_delete_installation(
        self, *, enterprise_id: Optional[str], team_id: Optional[str], user_id: Optional[str] = None
    ) -> None:
        self.delete_installation_called = True

    async def async_delete_all(self, *, enterprise_id: Optional[str], team_id: Optional[str]):
        self.delete_all_called = True
        return await super().async_delete_all(enterprise_id=enterprise_id, team_id=team_id)


class TestEventsTokenRevocations:
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
    async def test_no_installation_store(self):
        self.web_client.token = valid_token
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        with pytest.raises(BoltError):
            app.default_tokens_revoked_event_listener()
        with pytest.raises(BoltError):
            app.default_app_uninstalled_event_listener()
        with pytest.raises(BoltError):
            app.enable_token_revocation_listeners()

    @pytest.mark.asyncio
    async def test_tokens_revoked(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
            installation_store=MyInstallationStore(),
        )

        event_payload = {
            "token": "verification-token",
            "enterprise_id": "E111",
            "api_app_id": "A111",
            "event": {
                "type": "tokens_revoked",
                "tokens": {"oauth": ["W111"], "bot": ["W222"]},
            },
            "type": "event_callback",
            "event_id": "Ev111",
            "event_time": 1606805974,
        }

        timestamp, body = str(int(time())), json.dumps(event_payload)
        request: AsyncBoltRequest = AsyncBoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = await app.async_dispatch(request)
        assert response.status == 404

        # Enable the built-in event listeners
        app.enable_token_revocation_listeners()
        response = await app.async_dispatch(request)
        assert response.status == 200
        # auth.test API call must be skipped
        await assert_auth_test_count_async(self, 0)
        await asyncio.sleep(1)  # wait a bit after auto ack()
        assert app.installation_store.delete_bot_called is True
        assert app.installation_store.delete_installation_called is True
        assert app.installation_store.delete_all_called is False

    @pytest.mark.asyncio
    async def test_app_uninstalled(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
            installation_store=MyInstallationStore(),
        )

        event_payload = {
            "token": "verification-token",
            "enterprise_id": "E111",
            "api_app_id": "A111",
            "event": {"type": "app_uninstalled"},
            "type": "event_callback",
            "event_id": "Ev111",
            "event_time": 1606805974,
        }

        timestamp, body = str(int(time())), json.dumps(event_payload)
        request: AsyncBoltRequest = AsyncBoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = await app.async_dispatch(request)
        assert response.status == 404

        # Enable the built-in event listeners
        app.enable_token_revocation_listeners()
        response = await app.async_dispatch(request)
        assert response.status == 200
        # auth.test API call must be skipped
        await assert_auth_test_count_async(self, 0)
        await asyncio.sleep(1)  # wait a bit after auto ack()
        assert app.installation_store.delete_bot_called is True
        assert app.installation_store.delete_installation_called is True
        assert app.installation_store.delete_all_called is True
