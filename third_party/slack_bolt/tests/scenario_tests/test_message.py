import json
import re
import time

from slack_sdk.signature import SignatureVerifier
from slack_sdk.web import WebClient

from slack_bolt import BoltResponse
from slack_bolt.app import App
from slack_bolt.request import BoltRequest
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
    assert_auth_test_count,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestMessage:
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

    def build_request_from_body(self, message_body: dict) -> BoltRequest:
        timestamp, body = str(int(time.time())), json.dumps(message_body)
        return BoltRequest(body=body, headers=self.build_headers(timestamp, body))

    def build_request(self) -> BoltRequest:
        return self.build_request_from_body(message_body)

    def build_request2(self) -> BoltRequest:
        return self.build_request_from_body(message_body2)

    def build_request3(self) -> BoltRequest:
        return self.build_request_from_body(message_body3)

    def test_string_keyword(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.message("Hello")(whats_up)

        request = self.build_request()
        response = app.dispatch(request)
        assert response.status == 200
        assert_auth_test_count(self, 1)
        time.sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    def test_all_message_matching_1(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )

        @app.message("")
        def handle_all_new_messages(say):
            say("Thanks!")

        request = self.build_request2()
        response = app.dispatch(request)
        assert response.status == 200
        assert_auth_test_count(self, 1)
        time.sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    def test_all_message_matching_2(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )

        @app.message()
        def handle_all_new_messages(say):
            say("Thanks!")

        request = self.build_request2()
        response = app.dispatch(request)
        assert response.status == 200
        assert_auth_test_count(self, 1)
        time.sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    def test_string_keyword_capturing(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.message("We've received ([0-9]+) messages from (.+)!")(verify_matches)

        request = self.build_request2()
        response = app.dispatch(request)
        assert response.status == 200
        assert_auth_test_count(self, 1)
        time.sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    def test_string_keyword_capturing2(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.message(re.compile("We've received ([0-9]+) messages from (.+)!"))(verify_matches)

        request = self.build_request2()
        response = app.dispatch(request)
        assert response.status == 200
        assert_auth_test_count(self, 1)
        time.sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    def test_string_keyword_capturing_multi_capture(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.message(re.compile("([a-z|A-Z]{3,}-[0-9]+)"))(verify_matches_multi)

        request = self.build_request3()
        response = app.dispatch(request)
        assert response.status == 200
        assert_auth_test_count(self, 1)
        time.sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    def test_string_keyword_unmatched(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.message("HELLO")(whats_up)

        request = self.build_request()
        response = app.dispatch(request)
        assert response.status == 404
        assert_auth_test_count(self, 1)

    def test_regexp_keyword(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.message(re.compile("He.lo"))(whats_up)

        request = self.build_request()
        response = app.dispatch(request)
        assert response.status == 200
        assert_auth_test_count(self, 1)
        time.sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    def test_regexp_keyword_unmatched(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.message(re.compile("HELLO"))(whats_up)

        request = self.build_request()
        response = app.dispatch(request)
        assert response.status == 404
        assert_auth_test_count(self, 1)

    # https://github.com/slackapi/bolt-python/issues/232
    def test_issue_232_message_listener_middleware(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        called = {
            "first": False,
            "second": False,
        }

        def this_should_be_skipped():
            return BoltResponse(status=500, body="failed")

        @app.message("first", middleware=[this_should_be_skipped])
        def first():
            called["first"] = True

        @app.message("second", middleware=[])
        def second():
            called["second"] = True

        request = self.build_request_from_body(
            {
                "token": "verification_token",
                "team_id": "T111",
                "enterprise_id": "E111",
                "api_app_id": "A111",
                "event": {
                    "client_msg_id": "a8744611-0210-4f85-9f15-5faf7fb225c8",
                    "type": "message",
                    "text": "This message should match the second listener only",
                    "user": "W111",
                    "ts": "1596183880.004200",
                    "team": "T111",
                    "channel": "C111",
                    "event_ts": "1596183880.004200",
                    "channel_type": "channel",
                },
                "type": "event_callback",
                "event_id": "Ev111",
                "event_time": 1596183880,
            }
        )
        response = app.dispatch(request)
        assert response.status == 200
        assert called["first"] == False
        assert called["second"] == True

    def test_issue_561_matchers(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )

        def just_fail():
            raise "This matcher should not be called!"

        @app.message("xxx", matchers=[just_fail])
        def just_ack():
            raise "This listener should not be called!"

        request = self.build_request()
        response = app.dispatch(request)
        assert response.status == 404
        assert_auth_test_count(self, 1)


message_body = {
    "token": "verification_token",
    "team_id": "T111",
    "enterprise_id": "E111",
    "api_app_id": "A111",
    "event": {
        "client_msg_id": "a8744611-0210-4f85-9f15-5faf7fb225c8",
        "type": "message",
        "text": "Hello World!",
        "user": "W111",
        "ts": "1596183880.004200",
        "team": "T111",
        "blocks": [
            {
                "type": "rich_text",
                "block_id": "ezJ",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [{"type": "text", "text": "Hello World!"}],
                    }
                ],
            }
        ],
        "channel": "C111",
        "event_ts": "1596183880.004200",
        "channel_type": "channel",
    },
    "type": "event_callback",
    "event_id": "Ev111",
    "event_time": 1596183880,
    "authed_users": ["W111"],
}


def whats_up(body, payload, message, say):
    assert body == message_body
    assert payload == message
    say("What's up?")


message_body2 = {
    "token": "verification_token",
    "team_id": "T111",
    "enterprise_id": "E111",
    "api_app_id": "A111",
    "event": {
        "client_msg_id": "a8744611-0210-4f85-9f15-5faf7fb225c8",
        "type": "message",
        "text": "We've received 103 messages from you!",
        "user": "W111",
        "ts": "1596183880.004200",
        "team": "T111",
        "channel": "C111",
        "event_ts": "1596183880.004200",
        "channel_type": "channel",
    },
    "type": "event_callback",
    "event_id": "Ev111",
    "event_time": 1596183880,
    "authed_users": ["W111"],
}


message_body3 = {
    "token": "verification_token",
    "team_id": "T111",
    "enterprise_id": "E111",
    "api_app_id": "A111",
    "event": {
        "client_msg_id": "a8744611-0210-4f85-9f15-5faf7fb225c8",
        "type": "message",
        "text": "Please fix JIRA-1234, SCM-567 and BUG-169 as soon as you can!",
        "user": "W111",
        "ts": "1596183880.004200",
        "team": "T111",
        "channel": "C111",
        "event_ts": "1596183880.004200",
        "channel_type": "channel",
    },
    "type": "event_callback",
    "event_id": "Ev111",
    "event_time": 1596183880,
    "authed_users": ["W111"],
}


def verify_matches(context, say, body, payload, message):
    assert context["matches"] == ("103", "you")
    assert context.matches == ("103", "you")
    assert body["event"] == message
    assert payload == message
    say("Thanks!")


def verify_matches_multi(context, say, body, payload, message):
    assert context["matches"] == ("JIRA-1234", "SCM-567", "BUG-169")
    assert context.matches == ("JIRA-1234", "SCM-567", "BUG-169")
    assert body["event"] == message
    assert payload == message
    say("Thanks!")
