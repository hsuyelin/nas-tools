import json
from time import time
from urllib.parse import quote

from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier

from slack_bolt import BoltRequest, BoltContext
from slack_bolt.app import App
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
    assert_auth_test_count,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestBlockActions:
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
            "content-type": ["application/x-www-form-urlencoded"],
            "x-slack-signature": [self.generate_signature(body, timestamp)],
            "x-slack-request-timestamp": [timestamp],
        }

    def build_valid_request(self) -> BoltRequest:
        timestamp = str(int(time()))
        return BoltRequest(body=raw_body, headers=self.build_headers(timestamp, raw_body))

    def test_mock_server_is_running(self):
        resp = self.web_client.api_test()
        assert resp != None

    def test_success(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.action("a")(simple_listener)

        request = self.build_valid_request()
        response = app.dispatch(request)
        assert response.status == 200
        assert_auth_test_count(self, 1)

    def test_success_2(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.block_action("a")(simple_listener)

        request = self.build_valid_request()
        response = app.dispatch(request)
        assert response.status == 200
        assert_auth_test_count(self, 1)

    def test_process_before_response(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
            process_before_response=True,
        )
        app.action("a")(simple_listener)

        request = self.build_valid_request()
        response = app.dispatch(request)
        assert response.status == 200
        assert_auth_test_count(self, 1)

    def test_default_type(self):
        app = App(client=self.web_client, signing_secret=self.signing_secret)
        app.action({"action_id": "a", "block_id": "b"})(simple_listener)

        request = self.build_valid_request()
        response = app.dispatch(request)
        assert response.status == 200
        assert_auth_test_count(self, 1)

    def test_default_type_no_block_id(self):
        app = App(client=self.web_client, signing_secret=self.signing_secret)
        app.action({"action_id": "a"})(simple_listener)

        request = self.build_valid_request()
        response = app.dispatch(request)
        assert response.status == 200
        assert_auth_test_count(self, 1)

    def test_default_type_and_unmatched_block_id(self):
        app = App(client=self.web_client, signing_secret=self.signing_secret)
        app.action({"action_id": "a", "block_id": "bbb"})(simple_listener)

        request = self.build_valid_request()
        response = app.dispatch(request)
        assert response.status == 404
        assert_auth_test_count(self, 1)

    def test_failure(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        request = self.build_valid_request()
        response = app.dispatch(request)
        assert response.status == 404
        assert_auth_test_count(self, 1)

        app.action("aaa")(simple_listener)
        response = app.dispatch(request)
        assert response.status == 404
        assert_auth_test_count(self, 1)

    def test_failure_2(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        request = self.build_valid_request()
        response = app.dispatch(request)
        assert response.status == 404
        assert_auth_test_count(self, 1)

        app.block_action("aaa")(simple_listener)
        response = app.dispatch(request)
        assert response.status == 404
        assert_auth_test_count(self, 1)


body = {
    "type": "block_actions",
    "user": {
        "id": "W111",
        "username": "primary-owner",
        "name": "primary-owner",
        "team_id": "T111",
    },
    "api_app_id": "A111",
    "token": "verification_token",
    "container": {
        "type": "message",
        "message_ts": "111.222",
        "channel_id": "C111",
        "is_ephemeral": True,
    },
    "trigger_id": "111.222.valid",
    "team": {
        "id": "T111",
        "domain": "workspace-domain",
        "enterprise_id": "E111",
        "enterprise_name": "Sandbox Org",
    },
    "channel": {"id": "C111", "name": "test-channel"},
    "response_url": "https://hooks.slack.com/actions/T111/111/random-value",
    "actions": [
        {
            "action_id": "a",
            "block_id": "b",
            "text": {"type": "plain_text", "text": "Button", "emoji": True},
            "value": "click_me_123",
            "type": "button",
            "action_ts": "1596530385.194939",
        }
    ],
}

raw_body = f"payload={quote(json.dumps(body))}"


def simple_listener(ack, body, payload, action, context: BoltContext):
    assert body["trigger_id"] == "111.222.valid"
    assert body["actions"][0] == payload
    assert payload == action
    assert action["action_id"] == "a"
    assert context.bot_id == "BZYBOTHED"
    assert context.bot_user_id == "W23456789"
    assert context.bot_token == "xoxb-valid"
    assert context.token == "xoxb-valid"
    assert context.user_id == "W111"
    assert context.user_token is None
    ack()
