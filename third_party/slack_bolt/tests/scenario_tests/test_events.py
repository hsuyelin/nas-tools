import json
import re
from functools import wraps
from time import time, sleep

import pytest
from slack_sdk.signature import SignatureVerifier
from slack_sdk.web import WebClient

from slack_bolt import App, BoltRequest, Say, BoltContext
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
    assert_auth_test_count,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestEvents:
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

    def test_middleware(self):
        app = App(client=self.web_client, signing_secret=self.signing_secret)

        @app.event("app_mention")
        def handle_app_mention(body, say, payload, event):
            assert body == self.valid_event_body
            assert body["event"] == payload
            assert payload == event
            say("What's up?")

        timestamp, body = str(int(time())), json.dumps(self.valid_event_body)
        request: BoltRequest = BoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = app.dispatch(request)
        assert response.status == 200
        assert_auth_test_count(self, 1)
        sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    def test_middleware_skip(self):
        app = App(client=self.web_client, signing_secret=self.signing_secret)

        def skip_middleware(req, resp, next):
            # return next()
            pass

        @app.event("app_mention", middleware=[skip_middleware])
        def handle_app_mention(body, logger, payload, event):
            assert body["event"] == payload
            assert payload == event
            logger.info(payload)

        timestamp, body = str(int(time())), json.dumps(self.valid_event_body)
        request: BoltRequest = BoltRequest(body=body, headers=self.build_headers(timestamp, body))
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
        app = App(client=self.web_client, signing_secret=self.signing_secret)

        @app.event("reaction_added")
        def handle_app_mention(body, say, payload, event):
            assert body == self.valid_reaction_added_body
            assert body["event"] == payload
            assert payload == event
            say("What's up?")

        timestamp, body = str(int(time())), json.dumps(self.valid_reaction_added_body)
        request: BoltRequest = BoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = app.dispatch(request)
        assert response.status == 200
        assert_auth_test_count(self, 1)
        sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    def test_stable_auto_ack(self):
        app = App(client=self.web_client, signing_secret=self.signing_secret)

        @app.event("reaction_added")
        def handle_app_mention():
            raise Exception("Something wrong!")

        for _ in range(10):
            timestamp, body = (
                str(int(time())),
                json.dumps(self.valid_reaction_added_body),
            )
            request: BoltRequest = BoltRequest(body=body, headers=self.build_headers(timestamp, body))
            response = app.dispatch(request)
            assert response.status == 200

    def test_self_member_join_left_events(self):
        app = App(client=self.web_client, signing_secret=self.signing_secret)

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

        timestamp, body = str(int(time())), json.dumps(join_event_body)
        request: BoltRequest = BoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = app.dispatch(request)
        assert response.status == 200
        assert_auth_test_count(self, 1)

        timestamp, body = str(int(time())), json.dumps(left_event_body)
        request: BoltRequest = BoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = app.dispatch(request)
        assert response.status == 200

        sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 2

    def test_member_join_left_events(self):
        app = App(client=self.web_client, signing_secret=self.signing_secret)

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

        timestamp, body = str(int(time())), json.dumps(join_event_body)
        request: BoltRequest = BoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = app.dispatch(request)
        assert response.status == 200
        assert_auth_test_count(self, 1)

        timestamp, body = str(int(time())), json.dumps(left_event_body)
        request: BoltRequest = BoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = app.dispatch(request)
        assert response.status == 200

        sleep(1)  # wait a bit after auto ack()
        # the listeners should not be executed
        assert self.mock_received_requests["/chat.postMessage"] == 2

    def test_uninstallation_and_revokes(self):
        app = App(client=self.web_client, signing_secret=self.signing_secret)
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

        timestamp, body = str(int(time())), json.dumps(app_uninstalled_body)
        request: BoltRequest = BoltRequest(body=body, headers=self.build_headers(timestamp, body))
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

        timestamp, body = str(int(time())), json.dumps(tokens_revoked_body)
        request: BoltRequest = BoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = app.dispatch(request)
        assert response.status == 200

        assert_auth_test_count(self, 1)
        sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 2

    message_file_share_body = {
        "token": "verification-token",
        "team_id": "T111",
        "api_app_id": "A111",
        "event": {
            "type": "message",
            "text": "Here is your file!",
            "files": [
                {
                    "id": "F111",
                    "created": 1610493713,
                    "timestamp": 1610493713,
                    "name": "test.png",
                    "title": "test.png",
                    "mimetype": "image/png",
                    "filetype": "png",
                    "pretty_type": "PNG",
                    "user": "U111",
                    "editable": False,
                    "size": 42706,
                    "mode": "hosted",
                    "is_external": False,
                    "external_type": "",
                    "is_public": False,
                    "public_url_shared": False,
                    "display_as_bot": False,
                    "username": "",
                    "url_private": "https://files.slack.com/files-pri/T111-F111/test.png",
                    "url_private_download": "https://files.slack.com/files-pri/T111-F111/download/test.png",
                    "thumb_64": "https://files.slack.com/files-tmb/T111-F111-8d3f9a6d4b/test_64.png",
                    "thumb_80": "https://files.slack.com/files-tmb/T111-F111-8d3f9a6d4b/test_80.png",
                    "thumb_360": "https://files.slack.com/files-tmb/T111-F111-8d3f9a6d4b/test_360.png",
                    "thumb_360_w": 358,
                    "thumb_360_h": 360,
                    "thumb_480": "https://files.slack.com/files-tmb/T111-F111-8d3f9a6d4b/test_480.png",
                    "thumb_480_w": 477,
                    "thumb_480_h": 480,
                    "thumb_160": "https://files.slack.com/files-tmb/T111-F111-8d3f9a6d4b/test_160.png",
                    "thumb_720": "https://files.slack.com/files-tmb/T111-F111-8d3f9a6d4b/test_720.png",
                    "thumb_720_w": 716,
                    "thumb_720_h": 720,
                    "original_w": 736,
                    "original_h": 740,
                    "thumb_tiny": "xxx",
                    "permalink": "https://xxx.slack.com/files/U111/F111/test.png",
                    "permalink_public": "https://slack-files.com/T111-F111-3e534ef8ca",
                    "has_rich_preview": False,
                }
            ],
            "upload": False,
            "blocks": [
                {
                    "type": "rich_text",
                    "block_id": "gvM",
                    "elements": [
                        {
                            "type": "rich_text_section",
                            "elements": [{"type": "text", "text": "Here is your file!"}],
                        }
                    ],
                }
            ],
            "user": "U111",
            "display_as_bot": False,
            "ts": "1610493715.001000",
            "channel": "G111",
            "subtype": "file_share",
            "event_ts": "1610493715.001000",
            "channel_type": "group",
        },
        "type": "event_callback",
        "event_id": "Ev111",
        "event_time": 1610493715,
        "authorizations": [
            {
                "enterprise_id": None,
                "team_id": "T111",
                "user_id": "U111",
                "is_bot": True,
                "is_enterprise_install": False,
            }
        ],
        "is_ext_shared_channel": False,
        "event_context": "1-message-T111-G111",
    }

    def test_message_subtypes_0(self):
        app = App(client=self.web_client, signing_secret=self.signing_secret)
        app._client = WebClient(token="uninstalled-revoked", base_url=self.mock_api_server_base_url)

        @app.event({"type": "message", "subtype": "file_share"})
        def handler1(event):
            assert event["subtype"] == "file_share"

        timestamp, body = str(int(time())), json.dumps(self.message_file_share_body)
        request: BoltRequest = BoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = app.dispatch(request)
        assert response.status == 200

    def test_message_subtypes_1(self):
        app = App(client=self.web_client, signing_secret=self.signing_secret)
        app._client = WebClient(token="uninstalled-revoked", base_url=self.mock_api_server_base_url)

        @app.event({"type": "message", "subtype": re.compile("file_.+")})
        def handler1(event):
            assert event["subtype"] == "file_share"

        timestamp, body = str(int(time())), json.dumps(self.message_file_share_body)
        request: BoltRequest = BoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = app.dispatch(request)
        assert response.status == 200

    def test_message_subtypes_2(self):
        app = App(client=self.web_client, signing_secret=self.signing_secret)
        app._client = WebClient(token="uninstalled-revoked", base_url=self.mock_api_server_base_url)

        @app.event({"type": "message", "subtype": ["file_share"]})
        def handler1(event):
            assert event["subtype"] == "file_share"

        timestamp, body = str(int(time())), json.dumps(self.message_file_share_body)
        request: BoltRequest = BoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = app.dispatch(request)
        assert response.status == 200

    def test_message_subtypes_3(self):
        app = App(client=self.web_client, signing_secret=self.signing_secret)
        app._client = WebClient(token="uninstalled-revoked", base_url=self.mock_api_server_base_url)

        @app.event("message")
        def handler1(event):
            assert event["subtype"] == "file_share"

        timestamp, body = str(int(time())), json.dumps(self.message_file_share_body)
        request: BoltRequest = BoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = app.dispatch(request)
        assert response.status == 200

    # https://github.com/slackapi/bolt-python/issues/199
    def test_invalid_message_events(self):
        app = App(client=self.web_client, signing_secret=self.signing_secret)

        def handle():
            pass

        # valid
        app.event("message")(handle)

        with pytest.raises(ValueError):
            app.event("message.channels")(handle)
        with pytest.raises(ValueError):
            app.event("message.groups")(handle)
        with pytest.raises(ValueError):
            app.event("message.im")(handle)
        with pytest.raises(ValueError):
            app.event("message.mpim")(handle)

        with pytest.raises(ValueError):
            app.event(re.compile("message\\..*"))(handle)

        with pytest.raises(ValueError):
            app.event({"type": "message.channels"})(handle)
        with pytest.raises(ValueError):
            app.event({"type": re.compile("message\\..*")})(handle)

    def test_context_generation(self):
        body = {
            "token": "verification-token",
            "enterprise_id": "E222",  # intentionally inconsistent for testing
            "team_id": "T222",  # intentionally inconsistent for testing
            "api_app_id": "A111",
            "event": {
                "type": "member_left_channel",
                "user": "W111",
                "channel": "C111",
                "channel_type": "C",
                "team": "T111",
            },
            "type": "event_callback",
            "event_id": "Ev111",
            "event_time": 1610493715,
            "authorizations": [
                {
                    "enterprise_id": "E333",
                    "user_id": "W222",
                    "is_bot": True,
                    "is_enterprise_install": True,
                }
            ],
            "is_ext_shared_channel": False,
            "event_context": "1-message-T111-G111",
        }
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
            process_before_response=True,
        )

        @app.event("member_left_channel")
        def handle(context: BoltContext):
            assert context.enterprise_id == "E333"
            assert context.team_id is None
            assert context.is_enterprise_install is True
            assert context.user_id == "W111"

        timestamp, json_body = str(int(time())), json.dumps(body)
        request: BoltRequest = BoltRequest(body=json_body, headers=self.build_headers(timestamp, json_body))
        response = app.dispatch(request)
        assert response.status == 200

    def test_additional_decorators_1(self):
        app = App(client=self.web_client, signing_secret=self.signing_secret)

        @my_decorator
        @app.event("app_mention")
        def handle_app_mention(body, say, payload, event):
            assert body == self.valid_event_body
            assert body["event"] == payload
            assert payload == event
            say("What's up?")

        timestamp, body = str(int(time())), json.dumps(self.valid_event_body)
        request: BoltRequest = BoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = app.dispatch(request)
        assert response.status == 200
        assert_auth_test_count(self, 1)
        sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    def test_additional_decorators_2(self):
        app = App(client=self.web_client, signing_secret=self.signing_secret)

        @app.event("app_mention")
        @my_decorator
        def handle_app_mention(body, say, payload, event):
            assert body == self.valid_event_body
            assert body["event"] == payload
            assert payload == event
            say("What's up?")

        timestamp, body = str(int(time())), json.dumps(self.valid_event_body)
        request: BoltRequest = BoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = app.dispatch(request)
        assert response.status == 200
        assert_auth_test_count(self, 1)
        sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1


def my_decorator(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        f(*args, **kwargs)

    return wrap
