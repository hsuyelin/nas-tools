from slack_sdk import WebClient

from slack_bolt.app.app import SlackAppDevelopmentServer, App
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestDevServer:
    signing_secret = "secret"
    valid_token = "xoxb-valid"
    mock_api_server_base_url = "http://localhost:8888"
    web_client = WebClient(
        token=valid_token,
        base_url=mock_api_server_base_url,
    )

    def setup_method(self):
        self.old_os_env = remove_os_env_temporarily()
        setup_mock_web_api_server(self)

    def teardown_method(self):
        cleanup_mock_web_api_server(self)
        restore_os_env(self.old_os_env)

    def test_instance(self):
        server = SlackAppDevelopmentServer(
            port=3001,
            path="/slack/events",
            app=App(signing_secret=self.signing_secret, client=self.web_client),
        )
        assert server is not None
