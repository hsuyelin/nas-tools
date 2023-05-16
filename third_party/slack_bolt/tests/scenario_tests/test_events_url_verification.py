import json
from time import time

from slack_sdk.web import WebClient
from slack_sdk.signature import SignatureVerifier

from slack_bolt import App, BoltRequest
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
    assert_auth_test_count,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestEventsUrlVerification:
    valid_token = "xoxb-valid"
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

    def build_headers(self, timestamp: str, body: str):
        return {
            "content-type": ["application/json"],
            "x-slack-signature": [self.generate_signature(body, timestamp)],
            "x-slack-request-timestamp": [timestamp],
        }

    def test_default(self):
        app = App(client=self.web_client, signing_secret=self.signing_secret)

        timestamp, body = str(int(time())), json.dumps(event_body)
        request: BoltRequest = BoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = app.dispatch(request)
        assert response.status == 200
        assert response.body == """{"challenge": "3eZbrw1aBm2rZgRNFdxV2595E9CY3gmdALWMmHkvFXO7tYXAYM8P"}"""
        assert_auth_test_count(self, 0)

    def test_disabled(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
            url_verification_enabled=False,
        )

        timestamp, body = str(int(time())), json.dumps(event_body)
        request: BoltRequest = BoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = app.dispatch(request)
        assert response.status == 404
        assert response.body == """{"error": "unhandled request"}"""
        assert_auth_test_count(self, 0)


event_body = {
    "token": "Jhj5dZrVaK7ZwHHjRyZWjbDl",
    "challenge": "3eZbrw1aBm2rZgRNFdxV2595E9CY3gmdALWMmHkvFXO7tYXAYM8P",
    "type": "url_verification",
}
