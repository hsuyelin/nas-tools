import json
from time import sleep, time

from slack_sdk.web import WebClient
from slack_sdk.signature import SignatureVerifier

from slack_bolt import App, BoltRequest
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
    assert_auth_test_count,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestEventsRequestVerification:
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

        @app.event("reaction_added")
        def handle_app_mention(say):
            say("What's up?")

        timestamp, body = str(int(time())), json.dumps(event_body)
        request: BoltRequest = BoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = app.dispatch(request)
        assert response.status == 200
        assert_auth_test_count(self, 1)
        sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests.get("/chat.postMessage") == 1

    def test_disabled(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
            request_verification_enabled=False,
        )

        @app.event("reaction_added")
        def handle_app_mention(say):
            say("What's up?")

        # request including invalid headers
        expired = int(time()) - 3600
        timestamp, body = str(expired), json.dumps(event_body)
        request: BoltRequest = BoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = app.dispatch(request)
        assert response.status == 200
        assert_auth_test_count(self, 1)
        sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests.get("/chat.postMessage") == 1


event_body = {
    "token": "verification_token",
    "team_id": "T111",
    "enterprise_id": "E111",
    "api_app_id": "A111",
    "event": {
        "type": "reaction_added",
        "user": "W111",
        "item": {
            "type": "message",
            "channel": "C111",
            "ts": "1599529504.000400",
        },
        "reaction": "heart_eyes",
        "item_user": "W111",
        "event_ts": "1599616881.000800",
    },
    "type": "event_callback",
    "event_id": "Ev111",
    "event_time": 1599616881,
    "authed_users": ["W111"],
}
