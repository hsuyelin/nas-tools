from time import sleep

import pytest
from slack_sdk.web import WebClient

from slack_bolt import App, BoltRequest, Say
from slack_bolt.error import BoltError
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
    assert_auth_test_count,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestEventsSocketMode:
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

    valid_event_body = {
        "token": "verification_token",
        "team_id": "T111",
        "enterprise_id": "E111",
        "api_app_id": "A111",
        "event": {
            "client_msg_id": "9cbd4c5b-7ddf-4ede-b479-ad21fca66d63",
            "type": "app_mention",
            "text": "<@W111> Hi there!",
            "user": "W222",
            "ts": "1595926230.009600",
            "team": "T111",
            "channel": "C111",
            "event_ts": "1595926230.009600",
        },
        "type": "event_callback",
        "event_id": "Ev111",
        "event_time": 1595926230,
        "authed_users": ["W111"],
    }

    def test_mock_server_is_running(self):
        resp = self.web_client.api_test()
        assert resp != None

    def test_body_validation(self):
        with pytest.raises(BoltError):
            BoltRequest(body={"foo": "bar"}, mode="http")

    def test_middleware(self):
        app = App(client=self.web_client)

        @app.event("app_mention")
        def handle_app_mention(body, say, payload, event):
            assert body == self.valid_event_body
            assert body["event"] == payload
            assert payload == event
            say("What's up?")

        request: BoltRequest = BoltRequest(body=self.valid_event_body, mode="socket_mode")
        response = app.dispatch(request)
        assert response.status == 200
        assert_auth_test_count(self, 1)
        sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    def test_middleware_skip(self):
        app = App(client=self.web_client)

        def skip_middleware(req, resp, next):
            # return next()
            pass

        @app.event("app_mention", middleware=[skip_middleware])
        def handle_app_mention(body, logger, payload, event):
            assert body["event"] == payload
            assert payload == event
            logger.info(payload)

        request: BoltRequest = BoltRequest(body=self.valid_event_body, mode="socket_mode")
        response = app.dispatch(request)
        assert response.status == 404
        assert_auth_test_count(self, 1)

    valid_reaction_added_body = {
        "token": "verification_token",
        "team_id": "T111",
        "enterprise_id": "E111",
        "api_app_id": "A111",
        "event": {
            "type": "reaction_added",
            "user": "W111",
            "item": {"type": "message", "channel": "C111", "ts": "1599529504.000400"},
            "reaction": "heart_eyes",
            "item_user": "W111",
            "event_ts": "1599616881.000800",
        },
        "type": "event_callback",
        "event_id": "Ev111",
        "event_time": 1599616881,
        "authed_users": ["W111"],
    }

    def test_reaction_added(self):
        app = App(client=self.web_client)

        @app.event("reaction_added")
        def handle_app_mention(body, say, payload, event):
            assert body == self.valid_reaction_added_body
            assert body["event"] == payload
            assert payload == event
            say("What's up?")

        request: BoltRequest = BoltRequest(body=self.valid_reaction_added_body, mode="socket_mode")
        response = app.dispatch(request)
        assert response.status == 200
        assert_auth_test_count(self, 1)
        sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    def test_stable_auto_ack(self):
        app = App(client=self.web_client)

        @app.event("reaction_added")
        def handle_app_mention():
            raise Exception("Something wrong!")

        for _ in range(10):
            request: BoltRequest = BoltRequest(body=self.valid_reaction_added_body, mode="socket_mode")
            response = app.dispatch(request)
            assert response.status == 200

    def test_self_events(self):
        app = App(client=self.web_client)

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

    def test_self_member_join_left_events(self):
        app = App(client=self.web_client)

        join_event_body = {
            "token": "verification_token",
            "team_id": "T111",
            "enterprise_id": "E111",
            "api_app_id": "A111",
            "event": {
                "type": "member_joined_channel",
                "user": "W23456789",  # bot_user_id
                "channel": "C111",
                "channel_type": "C",
                "team": "T111",
                "inviter": "U222",
            },
            "type": "event_callback",
            "event_id": "Ev111",
            "event_time": 1599616881,
            "authed_users": ["W111"],
        }

        left_event_body = {
            "token": "verification_token",
            "team_id": "T111",
            "enterprise_id": "E111",
            "api_app_id": "A111",
            "event": {
                "type": "member_left_channel",
                "user": "W23456789",  # bot_user_id
                "channel": "C111",
                "channel_type": "C",
                "team": "T111",
            },
            "type": "event_callback",
            "event_id": "Ev111",
            "event_time": 1599616881,
            "authed_users": ["W111"],
        }

        @app.event("member_joined_channel")
        def handle_member_joined_channel(say):
            say("What's up?")

        @app.event("member_left_channel")
        def handle_member_left_channel(say):
            say("What's up?")

        request: BoltRequest = BoltRequest(body=join_event_body, mode="socket_mode")
        response = app.dispatch(request)
        assert response.status == 200
        assert_auth_test_count(self, 1)

        request: BoltRequest = BoltRequest(body=left_event_body, mode="socket_mode")
        response = app.dispatch(request)
        assert response.status == 200

        sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 2

    def test_member_join_left_events(self):
        app = App(client=self.web_client)

        join_event_body = {
            "token": "verification_token",
            "team_id": "T111",
            "enterprise_id": "E111",
            "api_app_id": "A111",
            "event": {
                "type": "member_joined_channel",
                "user": "U999",  # not self
                "channel": "C111",
                "channel_type": "C",
                "team": "T111",
                "inviter": "U222",
            },
            "type": "event_callback",
            "event_id": "Ev111",
            "event_time": 1599616881,
            "authed_users": ["W111"],
        }

        left_event_body = {
            "token": "verification_token",
            "team_id": "T111",
            "enterprise_id": "E111",
            "api_app_id": "A111",
            "event": {
                "type": "member_left_channel",
                "user": "U999",  # not self
                "channel": "C111",
                "channel_type": "C",
                "team": "T111",
            },
            "type": "event_callback",
            "event_id": "Ev111",
            "event_time": 1599616881,
            "authed_users": ["W111"],
        }

        @app.event("member_joined_channel")
        def handle_app_mention(say):
            say("What's up?")

        @app.event("member_left_channel")
        def handle_app_mention(say):
            say("What's up?")

        request: BoltRequest = BoltRequest(body=join_event_body, mode="socket_mode")
        response = app.dispatch(request)
        assert response.status == 200
        assert_auth_test_count(self, 1)

        request: BoltRequest = BoltRequest(body=left_event_body, mode="socket_mode")
        response = app.dispatch(request)
        assert response.status == 200

        sleep(1)  # wait a bit after auto ack()
        # the listeners should not be executed
        assert self.mock_received_requests["/chat.postMessage"] == 2

    def test_uninstallation_and_revokes(self):
        app = App(client=self.web_client)
        app._client = WebClient(token="uninstalled-revoked", base_url=self.mock_api_server_base_url)

        @app.event("app_uninstalled")
        def handler1(say: Say):
            say(channel="C111", text="What's up?")

        @app.event("tokens_revoked")
        def handler2(say: Say):
            say(channel="C111", text="What's up?")

        app_uninstalled_body = {
            "token": "verification_token",
            "team_id": "T111",
            "enterprise_id": "E111",
            "api_app_id": "A111",
            "event": {"type": "app_uninstalled"},
            "type": "event_callback",
            "event_id": "Ev111",
            "event_time": 1599616881,
        }

        request: BoltRequest = BoltRequest(body=app_uninstalled_body, mode="socket_mode")
        response = app.dispatch(request)
        assert response.status == 200

        tokens_revoked_body = {
            "token": "verification_token",
            "team_id": "T111",
            "enterprise_id": "E111",
            "api_app_id": "A111",
            "event": {
                "type": "tokens_revoked",
                "tokens": {"oauth": ["UXXXXXXXX"], "bot": ["UXXXXXXXX"]},
            },
            "type": "event_callback",
            "event_id": "Ev111",
            "event_time": 1599616881,
        }

        request: BoltRequest = BoltRequest(body=tokens_revoked_body, mode="socket_mode")
        response = app.dispatch(request)
        assert response.status == 200

        assert_auth_test_count(self, 1)
        sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 2
