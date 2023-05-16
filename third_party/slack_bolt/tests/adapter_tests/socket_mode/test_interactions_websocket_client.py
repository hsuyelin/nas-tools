import logging
import time

from slack_sdk import WebClient

from slack_bolt import App
from slack_bolt.adapter.socket_mode.websocket_client import SocketModeHandler
from .mock_socket_mode_server import (
    start_socket_mode_server,
    stop_socket_mode_server,
)
from .mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)
from ...utils import remove_os_env_temporarily, restore_os_env


class TestSocketModeWebsocketClient:
    logger = logging.getLogger(__name__)

    def setup_method(self):
        self.old_os_env = remove_os_env_temporarily()
        setup_mock_web_api_server(self)
        self.web_client = WebClient(
            token="xoxb-api_test",
            base_url="http://localhost:8888",
        )
        start_socket_mode_server(self, 3012)
        time.sleep(2)  # wait for the server

    def teardown_method(self):
        cleanup_mock_web_api_server(self)
        restore_os_env(self.old_os_env)
        stop_socket_mode_server(self)

    def test_interactions(self):

        app = App(client=self.web_client)

        result = {"shortcut": False, "command": False}

        @app.shortcut("do-something")
        def shortcut_handler(ack):
            result["shortcut"] = True
            ack()

        @app.command("/hello-socket-mode")
        def command_handler(ack):
            result["command"] = True
            ack()

        handler = SocketModeHandler(
            app_token="xapp-A111-222-xyz",
            app=app,
            trace_enabled=True,
        )
        try:
            handler.client.wss_uri = "ws://localhost:3012/link"

            handler.connect()
            assert handler.client.is_connected() is True
            time.sleep(2)  # wait for the message receiver

            handler.client.send_message("foo")

            time.sleep(2)
            assert result["shortcut"] is True
            assert result["command"] is True
        finally:
            handler.client.close()
