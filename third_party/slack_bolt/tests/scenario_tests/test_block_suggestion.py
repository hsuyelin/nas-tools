import copy
import json
from time import time
from urllib.parse import quote

from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier

from slack_bolt import BoltRequest
from slack_bolt.app import App
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
    assert_auth_test_count,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestBlockSuggestion:
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

    def build_valid_multi_request(self) -> BoltRequest:
        timestamp = str(int(time()))
        return BoltRequest(body=raw_multi_body, headers=self.build_headers(timestamp, raw_multi_body))

    def test_mock_server_is_running(self):
        resp = self.web_client.api_test()
        assert resp != None

    def test_success(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.options("es_a")(show_options)

        request = self.build_valid_request()
        response = app.dispatch(request)
        assert response.status == 200
        assert response.body == expected_response_body
        assert response.headers["content-type"][0] == "application/json;charset=utf-8"
        assert_auth_test_count(self, 1)

    def test_success_2(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.block_suggestion("es_a")(show_options)

        request = self.build_valid_request()
        response = app.dispatch(request)
        assert response.status == 200
        assert response.body == expected_response_body
        assert response.headers["content-type"][0] == "application/json;charset=utf-8"
        assert_auth_test_count(self, 1)

    def test_success_multi(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.options("mes_a")(show_multi_options)

        request = self.build_valid_multi_request()
        response = app.dispatch(request)
        assert response.status == 200
        assert response.body == expected_multi_response_body
        assert response.headers["content-type"][0] == "application/json;charset=utf-8"
        assert_auth_test_count(self, 1)

    def test_process_before_response(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
            process_before_response=True,
        )
        app.options("es_a")(show_options)

        request = self.build_valid_request()
        response = app.dispatch(request)
        assert response.status == 200
        assert response.body == expected_response_body
        assert response.headers["content-type"][0] == "application/json;charset=utf-8"
        assert_auth_test_count(self, 1)

    def test_process_before_response_multi(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
            process_before_response=True,
        )
        app.options("mes_a")(show_multi_options)

        request = self.build_valid_multi_request()
        response = app.dispatch(request)
        assert response.status == 200
        assert response.body == expected_multi_response_body
        assert response.headers["content-type"][0] == "application/json;charset=utf-8"
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

        app.options("mes_a")(show_multi_options)
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

        app.block_suggestion("mes_a")(show_multi_options)
        response = app.dispatch(request)
        assert response.status == 404
        assert_auth_test_count(self, 1)

    def test_failure_multi(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        request = self.build_valid_multi_request()
        response = app.dispatch(request)
        assert response.status == 404
        assert_auth_test_count(self, 1)

        app.options("es_a")(show_options)
        response = app.dispatch(request)
        assert response.status == 404
        assert_auth_test_count(self, 1)

    def test_empty_options(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.options("mes_a")(show_empty_options)

        request = self.build_valid_multi_request()
        response = app.dispatch(request)
        assert response.status == 200
        assert response.body == """{"options": []}"""
        assert response.headers["content-type"][0] == "application/json;charset=utf-8"
        assert_auth_test_count(self, 1)

    def test_empty_option_groups(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.options("mes_a")(show_empty_option_groups)

        request = self.build_valid_multi_request()
        response = app.dispatch(request)
        assert response.status == 200
        assert response.body == """{"option_groups": []}"""
        assert response.headers["content-type"][0] == "application/json;charset=utf-8"
        assert_auth_test_count(self, 1)


body = {
    "type": "block_suggestion",
    "user": {
        "id": "W111",
        "username": "primary-owner",
        "name": "primary-owner",
        "team_id": "T111",
    },
    "container": {"type": "view", "view_id": "V111"},
    "api_app_id": "A111",
    "token": "verification_token",
    "action_id": "es_a",
    "block_id": "es_b",
    "value": "search word",
    "team": {
        "id": "T111",
        "domain": "workspace-domain",
        "enterprise_id": "E111",
        "enterprise_name": "Sandbox Org",
    },
    "view": {
        "id": "V111",
        "team_id": "T111",
        "type": "modal",
        "blocks": [
            {
                "type": "input",
                "block_id": "5ar+",
                "label": {"type": "plain_text", "text": "Label"},
                "optional": False,
                "element": {"type": "plain_text_input", "action_id": "i5IpR"},
            },
            {
                "type": "input",
                "block_id": "es_b",
                "label": {"type": "plain_text", "text": "Search"},
                "optional": False,
                "element": {
                    "type": "external_select",
                    "action_id": "es_a",
                    "placeholder": {"type": "plain_text", "text": "Select an item"},
                },
            },
            {
                "type": "input",
                "block_id": "mes_b",
                "label": {"type": "plain_text", "text": "Search (multi)"},
                "optional": False,
                "element": {
                    "type": "multi_external_select",
                    "action_id": "mes_a",
                    "placeholder": {"type": "plain_text", "text": "Select an item"},
                },
            },
        ],
        "private_metadata": "",
        "callback_id": "view-id",
        "state": {"values": {}},
        "hash": "111.xxx",
        "title": {"type": "plain_text", "text": "My App"},
        "clear_on_close": False,
        "notify_on_close": False,
        "close": {"type": "plain_text", "text": "Cancel"},
        "submit": {"type": "plain_text", "text": "Submit"},
        "previous_view_id": None,
        "root_view_id": "V111",
        "app_id": "A111",
        "external_id": "",
        "app_installed_team_id": "T111",
        "bot_id": "B111",
    },
}

raw_body = f"payload={quote(json.dumps(body))}"

multi_body = copy.deepcopy(body)
multi_body["block_id"] = "mes_b"
multi_body["action_id"] = "mes_a"
raw_multi_body = f"payload={quote(json.dumps(multi_body))}"

response = {"options": [{"text": {"type": "plain_text", "text": "Maru"}, "value": "maru"}]}
expected_response_body = json.dumps(response)

multi_response = {
    "option_groups": [
        {
            "label": {"type": "plain_text", "text": "Group 1"},
            "options": [
                {"text": {"type": "plain_text", "text": "Option 1"}, "value": "1-1"},
                {"text": {"type": "plain_text", "text": "Option 2"}, "value": "1-2"},
            ],
        },
        {
            "label": {"type": "plain_text", "text": "Group 2"},
            "options": [
                {"text": {"type": "plain_text", "text": "Option 1"}, "value": "2-1"},
            ],
        },
    ]
}
expected_multi_response_body = json.dumps(multi_response)


def show_options(ack, body, payload, options):
    assert body == options
    assert payload == options
    ack(response)


def show_multi_options(ack, body, payload, options):
    assert body == options
    assert payload == options
    ack(multi_response)


def show_empty_options(ack, body, payload, options):
    assert body == options
    assert payload == options
    ack(options=[])


def show_empty_option_groups(ack, body, payload, options):
    assert body == options
    assert payload == options
    ack(option_groups=[])
