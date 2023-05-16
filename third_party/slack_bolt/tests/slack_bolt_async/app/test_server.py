from slack_bolt.app.async_app import AsyncApp
from slack_bolt.app.async_server import AsyncSlackAppServer


class TestServer:
    def setup_method(self):
        pass

    def teardown_method(self):
        pass

    def test_instance(self):
        server = AsyncSlackAppServer(
            port=3001,
            path="/slack/events",
            app=AsyncApp(
                signing_secret="valid",
                token="xoxb-valid",
            ),
        )
        assert server is not None
