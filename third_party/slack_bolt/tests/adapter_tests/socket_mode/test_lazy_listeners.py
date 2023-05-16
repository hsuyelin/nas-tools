import logging
import time

from slack_sdk import WebClient

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from .mock_socket_mode_server import (
    start_socket_mode_server,
    stop_socket_mode_server,
)
from .mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)
from ...utils import remove_os_env_temporarily, restore_os_env


class TestSocketModeLazyListeners:
    logger = logging.getLogger(__name__)

    def setup_method(self):
        self.old_os_env = remove_os_env_temporarily()
        setup_mock_web_api_server(self)
        self.web_client = WebClient(
            token="xoxb-api_test",
            base_url="http://localhost:8888",
        )
        start_socket_mode_server(self, 3011)
        time.sleep(2)  # wait for the server

    def teardown_method(self):
        cleanup_mock_web_api_server(self)
        restore_os_env(self.old_os_env)
        stop_socket_mode_server(self)

    def test_lazy_listener_calls(self):

        app = App(client=self.web_client)

        result = {"lazy_called": False}

        @app.shortcut("do-something")
        def handle_shortcuts(ack):
            ack()

        @app.event("message")
        def handle_message_events(body, logger):
            logger.info(body)

        def lazy_func(body):
            assert body.get("command") == "/hello-socket-mode"
            result["lazy_called"] = True

        app.command("/hello-socket-mode")(
            ack=lambda ack: ack(),
            lazy=[lazy_func],
        )

        handler = SocketModeHandler(
            app_token="xapp-A111-222-xyz",
            app=app,
            trace_enabled=True,
        )
        try:
            handler.client.wss_uri = "ws://127.0.0.1:3011/link"
            handler.connect()
            assert handler.client.is_connected() is True
            time.sleep(2)  # wait for the message receiver
            handler.client.send_message("foo")

            spent_time = 0
            while spent_time < 5 and result["lazy_called"] is False:
                spent_time += 0.5
                time.sleep(0.5)
            assert result["lazy_called"] is True

        finally:
            handler.client.close()
