import asyncio

import pytest
from slack_sdk.web.async_client import AsyncWebClient

from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from slack_bolt.app.async_app import AsyncApp
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)
from tests.utils import remove_os_env_temporarily, restore_os_env
from ...adapter_tests.socket_mode.mock_socket_mode_server import (
    start_socket_mode_server,
    stop_socket_mode_server_async,
)


class TestSocketModeAiohttp:
    valid_token = "xoxb-valid"
    mock_api_server_base_url = "http://localhost:8888"
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

    @pytest.mark.asyncio
    async def test_events(self):
        start_socket_mode_server(self, 3021)
        await asyncio.sleep(1)  # wait for the server

        app = AsyncApp(client=self.web_client)

        result = {"shortcut": False, "command": False}

        @app.shortcut("do-something")
        async def shortcut_handler(ack):
            result["shortcut"] = True
            await ack()

        @app.command("/hello-socket-mode")
        async def command_handler(ack):
            result["command"] = True
            await ack()

        handler = AsyncSocketModeHandler(
            app_token="xapp-A111-222-xyz",
            app=app,
        )
        try:
            handler.client.wss_uri = "ws://localhost:3021/link"

            await handler.connect_async()
            await asyncio.sleep(2)  # wait for the message receiver

            await handler.client.send_message("foo")

            await asyncio.sleep(2)
            assert result["shortcut"] is True
            assert result["command"] is True
        finally:
            await handler.client.close()
            await stop_socket_mode_server_async(self)
