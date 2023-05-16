import json
import time

from slack_sdk.signature import SignatureVerifier
from slack_sdk.web import WebClient

from slack_bolt.app import App
from slack_bolt.request import BoltRequest
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestMessageDeleted:
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

    def test_user_and_channel_id_in_context(self):
        app = App(client=self.web_client, signing_secret=self.signing_secret, process_before_response=True)

        @app.event({"type": "message", "subtype": "message_deleted"})
        def handle_message_deleted(context):
            # These should come from the main event payload part
            assert context.channel_id == "C111"
            assert context.user_id == "U111"
            # The following ones come from authorizations[0]
            assert context.team_id == "T-auth"
            assert context.enterprise_id == "E-auth"

        request = self.build_request(event_payload)
        response = app.dispatch(request)
        assert response.status == 200


event_payload = {
    "token": "verification-token",
    "team_id": "T111",
    "enterprise_id": "E111",
    "api_app_id": "A111",
    "event": {
        "type": "message",
        "subtype": "message_deleted",
        "previous_message": {
            "type": "message",
            "text": "Delete this message",
            "user": "U111",
            "team": "T111",
            "ts": "1665368619.804829",
        },
        "channel": "C111",
        "hidden": True,
        "deleted_ts": "1665368619.804829",
        "event_ts": "1665368629.007100",
        "ts": "1665368629.007100",
        "channel_type": "channel",
    },
    "type": "event_callback",
    "event_id": "Ev111",
    "event_time": 1665368629,
    "authorizations": [
        {
            "enterprise_id": "E-auth",
            "team_id": "T-auth",
            "user_id": "U-auth",
            "is_bot": True,
            "is_enterprise_install": False,
        }
    ],
    "is_ext_shared_channel": False,
    "event_context": "1-message-T111-C111",
}
