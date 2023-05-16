from time import sleep

from slack_sdk.web import WebClient

from slack_bolt import App, BoltRequest
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
    assert_auth_test_count,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestEventsIgnoreSelf:
    valid_token = "xoxb-valid"
    mock_api_server_base_url = "http://localhost:8888"
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

    def test_self_events(self):
        app = App(client=self.web_client)

        @app.event("reaction_added")
        def handle_app_mention(say):
            say("What's up?")

        request: BoltRequest = BoltRequest(body=event_body, mode="socket_mode")
        response = app.dispatch(request)
        assert response.status == 200
        assert_auth_test_count(self, 1)
        sleep(1)  # wait a bit after auto ack()
        # The listener should not be executed
        assert self.mock_received_requests.get("/chat.postMessage") is None

    def test_self_events_response_url(self):
        app = App(client=self.web_client)

        @app.event("message")
        def handle_app_mention(say):
            say("What's up?")

        request: BoltRequest = BoltRequest(body=response_url_message_event, mode="socket_mode")
        response = app.dispatch(request)
        assert response.status == 200
        assert_auth_test_count(self, 1)
        sleep(1)  # wait a bit after auto ack()
        # The listener should not be executed
        assert self.mock_received_requests.get("/chat.postMessage") is None

    def test_not_self_events_response_url(self):
        app = App(client=self.web_client)

        @app.event("message")
        def handle_app_mention(say):
            say("What's up?")

        request: BoltRequest = BoltRequest(body=different_app_response_url_message_event, mode="socket_mode")
        response = app.dispatch(request)
        assert response.status == 200
        assert_auth_test_count(self, 1)
        sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests.get("/chat.postMessage") == 1

    def test_self_events_disabled(self):
        app = App(
            client=self.web_client,
            ignoring_self_events_enabled=False,
        )

        @app.event("reaction_added")
        def handle_app_mention(say):
            say("What's up?")

        request: BoltRequest = BoltRequest(body=event_body, mode="socket_mode")
        response = app.dispatch(request)
        assert response.status == 200
        assert_auth_test_count(self, 1)
        sleep(1)  # wait a bit after auto ack()
        # The listener should be executed as the ignoring logic is disabled
        assert self.mock_received_requests.get("/chat.postMessage") == 1


event_body = {
    "token": "verification_token",
    "team_id": "T111",
    "enterprise_id": "E111",
    "api_app_id": "A111",
    "event": {
        "type": "reaction_added",
        "user": "W23456789",  # bot_user_id
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

response_url_message_event = {
    "token": "verification_token",
    "team_id": "T111",
    "enterprise_id": "E111",
    "api_app_id": "A111",
    "event": {
        "type": "message",
        "subtype": "bot_message",
        "text": "Hi there! This is a reply using response_url.",
        "ts": "1658282075.825129",
        "bot_id": "BZYBOTHED",
        "channel": "C111",
        "event_ts": "1658282075.825129",
        "channel_type": "channel",
    },
    "type": "event_callback",
    "event_id": "Ev111",
    "event_time": 1599616881,
    "authed_users": ["W111"],
}

different_app_response_url_message_event = {
    "token": "verification_token",
    "team_id": "T111",
    "enterprise_id": "E111",
    "api_app_id": "A111",
    "event": {
        "type": "message",
        "subtype": "bot_message",
        "text": "Hi there! This is a reply using response_url.",
        "ts": "1658282075.825129",
        "bot_id": "B_DIFFERENT_ONE",
        "channel": "C111",
        "event_ts": "1658282075.825129",
        "channel_type": "channel",
    },
    "type": "event_callback",
    "event_id": "Ev111",
    "event_time": 1599616881,
    "authed_users": ["W111"],
}
