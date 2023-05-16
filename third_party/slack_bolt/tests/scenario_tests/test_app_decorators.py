from typing import Callable

from slack_sdk import WebClient

from slack_bolt import App, Ack, BoltResponse
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class NoopAck(Ack):
    def __call__(self) -> BoltResponse:
        pass


class TestAppDecorators:
    signing_secret = "secret"
    valid_token = "xoxb-valid"
    mock_api_server_base_url = "http://localhost:8888"
    web_client = WebClient(token=valid_token, base_url=mock_api_server_base_url)

    def test_decorators(self):
        try:
            self.old_os_env = remove_os_env_temporarily()
            setup_mock_web_api_server(self)

            app = App(signing_secret=self.signing_secret, client=self.web_client)
            ack = NoopAck()

            @app.event("app_home_opened")
            def handle_events(body: dict):
                assert body is not None

            handle_events({})
            assert isinstance(handle_events, Callable)

            @app.message("hi")
            def handle_message_events(body: dict):
                assert body is not None

            handle_message_events({})
            assert isinstance(handle_message_events, Callable)

            @app.command("/hello")
            def handle_commands(ack: Ack, body: dict):
                assert body is not None
                ack()

            handle_commands(ack, {})
            assert isinstance(handle_commands, Callable)

            @app.shortcut("test-shortcut")
            def handle_shortcuts(ack: Ack, body: dict):
                assert body is not None
                ack()

            handle_shortcuts(ack, {})
            assert isinstance(handle_shortcuts, Callable)

            @app.action("some-action-id")
            def handle_actions(ack: Ack, body: dict):
                assert body is not None
                ack()

            handle_actions(ack, {})
            assert isinstance(handle_actions, Callable)

            @app.view("some-callback-id")
            def handle_views(ack: Ack, body: dict):
                assert body is not None
                ack()

            handle_views(ack, {})
            assert isinstance(handle_views, Callable)

            @app.options("some-id")
            def handle_views(ack: Ack, body: dict):
                assert body is not None
                ack()

            handle_views(ack, {})
            assert isinstance(handle_views, Callable)

            @app.error
            def handle_errors(body: dict):
                assert body is not None

            handle_errors({})
            assert isinstance(handle_errors, Callable)

            @app.use
            def middleware(body, next):
                assert body is not None
                next()

            def next_func():
                pass

            middleware({}, next_func)
            assert isinstance(middleware, Callable)

        finally:
            cleanup_mock_web_api_server(self)
            restore_os_env(self.old_os_env)
