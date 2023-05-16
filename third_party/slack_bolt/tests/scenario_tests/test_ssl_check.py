from time import time

from slack_sdk.signature import SignatureVerifier
from slack_sdk.web import WebClient

from slack_bolt import App, BoltRequest
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestSSLCheck:
    signing_secret = "secret"
    valid_token = "xoxb-valid"
    mock_api_server_base_url = "http://localhost:8888"
    signature_verifier = SignatureVerifier(signing_secret)
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

    def generate_signature(self, body: str, timestamp: str):
        return self.signature_verifier.generate_signature(
            body=body,
            timestamp=timestamp,
        )

    def test_mock_server_is_running(self):
        resp = self.web_client.api_test()
        assert resp != None

    def test_ssl_check(self):
        app = App(client=self.web_client, signing_secret=self.signing_secret)

        timestamp, body = str(int(time())), "token=random&ssl_check=1"
        request: BoltRequest = BoltRequest(
            body=body,
            query={},
            headers={
                "content-type": ["application/x-www-form-urlencoded"],
                "x-slack-signature": [self.generate_signature(body, timestamp)],
                "x-slack-request-timestamp": [timestamp],
            },
        )
        response = app.dispatch(request)
        assert response.status == 200
        assert response.body == ""

    def test_ssl_check_disabled(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
            ssl_check_enabled=False,
        )

        timestamp, body = str(int(time())), "token=random&ssl_check=1"
        request: BoltRequest = BoltRequest(
            body=body,
            query={},
            headers={
                "content-type": ["application/x-www-form-urlencoded"],
                "x-slack-signature": [self.generate_signature(body, timestamp)],
                "x-slack-request-timestamp": [timestamp],
            },
        )
        response = app.dispatch(request)
        assert response.status == 404
        assert response.body == """{"error": "unhandled request"}"""
