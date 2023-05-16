import asyncio

import pytest
from slack_sdk.web.async_client import AsyncWebClient

from slack_bolt.app.async_app import AsyncApp
from slack_bolt.request.async_request import AsyncBoltRequest
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestAsyncAppDispatch:
    signing_secret = "secret"
    valid_token = "xoxb-valid"
    mock_api_server_base_url = "http://localhost:8888"
    web_client = AsyncWebClient(token=valid_token, base_url=mock_api_server_base_url)

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

    @pytest.mark.asyncio
    async def test_none_body(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )

        req = AsyncBoltRequest(body=None, headers={}, mode="http")
        response = await app.async_dispatch(req)
        # request verification failure
        assert response.status == 401
        assert response.body == '{"error": "invalid request"}'

        req = AsyncBoltRequest(body=None, headers={}, mode="socket_mode")
        response = await app.async_dispatch(req)
        # request verification is skipped for Socket Mode
        assert response.status == 404
        assert response.body == '{"error": "unhandled request"}'

    @pytest.mark.asyncio
    async def test_none_body_no_middleware(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
            ssl_check_enabled=False,
            ignoring_self_events_enabled=False,
            request_verification_enabled=False,
            # token_verification_enabled=False,
            url_verification_enabled=False,
        )

        req = AsyncBoltRequest(body=None, headers={}, mode="http")
        response = await app.async_dispatch(req)
        assert response.status == 404
        assert response.body == '{"error": "unhandled request"}'

        req = AsyncBoltRequest(body=None, headers={}, mode="socket_mode")
        response = await app.async_dispatch(req)
        assert response.status == 404
        assert response.body == '{"error": "unhandled request"}'
