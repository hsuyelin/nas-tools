import json
import time

from slack_sdk.signature import SignatureVerifier
from slack_sdk.web import WebClient

from slack_bolt.app import App
from slack_bolt.request import BoltRequest
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
    assert_auth_test_count,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestMessageThreadBroadcast:
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

    def build_request(self, event_payload: dict) -> BoltRequest:
        timestamp, body = str(int(time.time())), json.dumps(event_payload)
        return BoltRequest(body=body, headers=self.build_headers(timestamp, body))

    def test_message_handler(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )

        result = {"call_count": 0}

        @app.message("Hi there!")
        def handle_messages(event, logger):
            logger.info(event)
            result["call_count"] = result["call_count"] + 1

        request = self.build_request(event_payload)
        response = app.dispatch(request)
        assert response.status == 200

        request = self.build_request(event_payload)
        response = app.dispatch(request)
        assert response.status == 200

        assert_auth_test_count(self, 1)
        time.sleep(1)  # wait a bit after auto ack()
        assert result["call_count"] == 2


event_payload = {
    "token": "verification-token",
    "team_id": "T111",
    "enterprise_id": "E111",
    "api_app_id": "A111",
    "event": {
        "type": "message",
        "subtype": "thread_broadcast",
        "text": "Hi there!",
        "user": "U111",
        "ts": "1633670813.007500",
        "thread_ts": "1633663824.000500",
        "root": {
            "client_msg_id": "111-222-333-444-555",
            "type": "message",
            "text": "Write in the thread :bow:",
            "user": "U111",
            "ts": "1633663824.000500",
            "team": "T111",
            "thread_ts": "1633663824.000500",
            "reply_count": 17,
            "reply_users_count": 1,
            "latest_reply": "1633670813.007500",
            "reply_users": ["U111"],
            "is_locked": False,
        },
        "client_msg_id": "111-222-333-444-666",
        "channel": "C111",
        "event_ts": "1633670813.007500",
        "channel_type": "channel",
    },
    "type": "event_callback",
    "event_id": "Ev111",
    "event_time": 1610261659,
    "authorizations": [
        {
            "enterprise_id": "E111",
            "team_id": "T111",
            "user_id": "W111",
            "is_bot": True,
            "is_enterprise_install": False,
        }
    ],
    "is_ext_shared_channel": False,
    "event_context": "1-message-T111-C111",
}
