from typing import Callable

import pytest
from slack_sdk.web.async_client import AsyncWebClient

from slack_bolt import BoltResponse
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.context.ack.async_ack import AsyncAck
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class NoopAsyncAck(AsyncAck):
    async def __call__(self) -> BoltResponse:
        pass


class TestAppDecorators:
    signing_secret = "secret"
    valid_token = "xoxb-valid"
    mock_api_server_base_url = "http://localhost:8888"
    web_client = AsyncWebClient(token=valid_token, base_url=mock_api_server_base_url)

    @pytest.mark.asyncio
    async def test_decorators(self):
        try:
            self.old_os_env = remove_os_env_temporarily()
            setup_mock_web_api_server(self)

            app = AsyncApp(signing_secret=self.signing_secret, client=self.web_client)
            ack = NoopAsyncAck()

            @app.event("app_home_opened")
            async def handle_events(body: dict):
                assert body is not None

            await handle_events({})
            assert isinstance(handle_events, Callable)

            @app.message("hi")
            async def handle_message_events(body: dict):
                assert body is not None

            await handle_message_events({})
            assert isinstance(handle_message_events, Callable)

            @app.command("/hello")
            async def handle_commands(ack: AsyncAck, body: dict):
                assert body is not None
                await ack()

            await handle_commands(ack, {})
            assert isinstance(handle_commands, Callable)

            @app.shortcut("test-shortcut")
            async def handle_shortcuts(ack: AsyncAck, body: dict):
                assert body is not None
                await ack()

            await handle_shortcuts(ack, {})
            assert isinstance(handle_shortcuts, Callable)

            @app.action("some-action-id")
            async def handle_actions(ack: AsyncAck, body: dict):
                assert body is not None
                await ack()

            await handle_actions(ack, {})
            assert isinstance(handle_actions, Callable)

            @app.view("some-callback-id")
            async def handle_views(ack: AsyncAck, body: dict):
                assert body is not None
                await ack()

            await handle_views(ack, {})
            assert isinstance(handle_views, Callable)

            @app.options("some-id")
            async def handle_views(ack: AsyncAck, body: dict):
                assert body is not None
                await ack()

            await handle_views(ack, {})
            assert isinstance(handle_views, Callable)

            @app.error
            async def handle_errors(body: dict):
                assert body is not None

            await handle_errors({})
            assert isinstance(handle_errors, Callable)

            @app.use
            async def middleware(body, next):
                assert body is not None
                await next()

            async def next_func():
                pass

            await middleware({}, next_func)
            assert isinstance(middleware, Callable)

        finally:
            cleanup_mock_web_api_server(self)
            restore_os_env(self.old_os_env)
