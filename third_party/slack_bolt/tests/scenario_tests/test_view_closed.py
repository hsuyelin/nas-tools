import json
from time import time
from urllib.parse import quote

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


class TestViewClosed:
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
        app.view({"type": "view_closed", "callback_id": "view-id"})(simple_listener)

        request = self.build_valid_request()
        response = app.dispatch(request)
        assert response.status == 200
        assert_auth_test_count(self, 1)

    def test_success_2(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.view_closed("view-id")(simple_listener)

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
        app.view({"type": "view_closed", "callback_id": "view-id"})(simple_listener)

        request = self.build_valid_request()
        response = app.dispatch(request)
        assert response.status == 200
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

        app.view("view-idddd")(simple_listener)
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

        app.view({"type": "view_closed", "callback_id": "view-idddd"})(simple_listener)
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

        app.view_closed("view-idddd")(simple_listener)
        response = app.dispatch(request)
        assert response.status == 404
        assert_auth_test_count(self, 1)


body = {
    "type": "view_closed",
    "team": {
        "id": "T111",
        "domain": "workspace-domain",
        "enterprise_id": "E111",
        "enterprise_name": "Sandbox Org",
    },
    "user": {
        "id": "W111",
        "username": "primary-owner",
        "name": "primary-owner",
        "team_id": "T111",
    },
    "api_app_id": "A111",
    "token": "verification_token",
    "view": {
        "id": "V111",
        "team_id": "T111",
        "type": "modal",
        "blocks": [
            {
                "type": "input",
                "block_id": "hspI",
                "label": {
                    "type": "plain_text",
                    "text": "Label",
                },
                "optional": False,
                "element": {"type": "plain_text_input", "action_id": "maBWU"},
            }
        ],
        "private_metadata": "This is for you!",
        "callback_id": "view-id",
        "state": {"values": {}},
        "hash": "1596530361.3wRYuk3R",
        "title": {
            "type": "plain_text",
            "text": "My App",
        },
        "clear_on_close": False,
        "notify_on_close": False,
        "close": {
            "type": "plain_text",
            "text": "Cancel",
        },
        "submit": {
            "type": "plain_text",
            "text": "Submit",
        },
        "previous_view_id": None,
        "root_view_id": "V111",
        "app_id": "A111",
        "external_id": "",
        "app_installed_team_id": "T111",
        "bot_id": "B111",
    },
    "response_urls": [],
}

raw_body = f"payload={quote(json.dumps(body))}"


def simple_listener(ack, body, payload, view):
    assert body["view"] == payload
    assert payload == view
    assert view["private_metadata"] == "This is for you!"
    ack()
