import asyncio
import json
import re
from functools import wraps
from random import random
from time import time

import pytest
from slack_sdk.signature import SignatureVerifier
from slack_sdk.web.async_client import AsyncWebClient

from slack_bolt.app.async_app import AsyncApp
from slack_bolt.context.async_context import AsyncBoltContext
from slack_bolt.context.say.async_say import AsyncSay
from slack_bolt.request.async_request import AsyncBoltRequest
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
    assert_auth_test_count_async,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestAsyncEvents:
    signing_secret = "secret"
    valid_token = "xoxb-valid"
    mock_api_server_base_url = "http://localhost:8888"
    signature_verifier = SignatureVerifier(signing_secret)
    web_client = AsyncWebClient(
        token=valid_token,
        base_url=mock_api_server_base_url,
    )

    @pytest.fixture
    def event_loop(self):
        old_os_env = remove_os_env_temporarily()
        try:
            setup_mock_web_api_server(self)
            loop = asyncio.get_event_loop()
            yield loop
            loop.close()
            cleanup_mock_web_api_server(self)
        finally:
            restore_os_env(old_os_env)

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

    def build_valid_app_mention_request(self) -> AsyncBoltRequest:
        timestamp, body = str(int(time())), json.dumps(app_mention_body)
        return AsyncBoltRequest(body=body, headers=self.build_headers(timestamp, body))

    @pytest.mark.asyncio
    async def test_mock_server_is_running(self):
        resp = await self.web_client.api_test()
        assert resp != None

    @pytest.mark.asyncio
    async def test_app_mention(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.event("app_mention")(whats_up)

        request = self.build_valid_app_mention_request()
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)
        await asyncio.sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    @pytest.mark.asyncio
    async def test_process_before_response(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
            process_before_response=True,
        )
        app.event("app_mention")(whats_up)

        request = self.build_valid_app_mention_request()
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)
        # no sleep here
        assert self.mock_received_requests["/chat.postMessage"] == 1

    @pytest.mark.asyncio
    async def test_middleware_skip(self):
        app = AsyncApp(client=self.web_client, signing_secret=self.signing_secret)
        app.event("app_mention", middleware=[skip_middleware])(whats_up)

        request = self.build_valid_app_mention_request()
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_simultaneous_requests(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.event("app_mention")(random_sleeper)

        request = self.build_valid_app_mention_request()

        times = 10
        tasks = []
        for i in range(times):
            tasks.append(asyncio.ensure_future(app.async_dispatch(request)))

        await asyncio.sleep(5)
        # Verifies all the tasks have been completed with 200 OK
        assert sum([t.result().status for t in tasks if t.done()]) == 200 * times

        assert self.mock_received_requests["/auth.test"] == times
        assert self.mock_received_requests["/chat.postMessage"] == times

    def build_valid_reaction_added_request(self) -> AsyncBoltRequest:
        timestamp, body = str(int(time())), json.dumps(reaction_added_body)
        return AsyncBoltRequest(body=body, headers=self.build_headers(timestamp, body))

    @pytest.mark.asyncio
    async def test_reaction_added(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.event("reaction_added")(whats_up)

        request = self.build_valid_reaction_added_request()
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)
        await asyncio.sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    @pytest.mark.asyncio
    async def test_stable_auto_ack(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.event("reaction_added")(always_failing)

        for _ in range(10):
            request = self.build_valid_reaction_added_request()
            response = await app.async_dispatch(request)
            assert response.status == 200

    @pytest.mark.asyncio
    async def test_self_joined_left_events(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.event("reaction_added")(whats_up)

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
        async def handle_member_joined_channel(say):
            await say("What's up?")

        @app.event("member_left_channel")
        async def handle_member_left_channel(say):
            await say("What's up?")

        timestamp, body = str(int(time())), json.dumps(join_event_body)
        request = AsyncBoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)

        timestamp, body = str(int(time())), json.dumps(left_event_body)
        request = AsyncBoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = await app.async_dispatch(request)
        assert response.status == 200

        await asyncio.sleep(1)  # wait a bit after auto ack()
        # The listeners should be executed
        assert self.mock_received_requests.get("/chat.postMessage") == 2

    @pytest.mark.asyncio
    async def test_joined_left_events(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.event("reaction_added")(whats_up)

        join_event_body = {
            "token": "verification_token",
            "team_id": "T111",
            "enterprise_id": "E111",
            "api_app_id": "A111",
            "event": {
                "type": "member_joined_channel",
                "user": "W111",  # other user
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
                "user": "W111",  # other user
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
        async def handle_member_joined_channel(say):
            await say("What's up?")

        @app.event("member_left_channel")
        async def handle_member_left_channel(say):
            await say("What's up?")

        timestamp, body = str(int(time())), json.dumps(join_event_body)
        request = AsyncBoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)

        timestamp, body = str(int(time())), json.dumps(left_event_body)
        request = AsyncBoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = await app.async_dispatch(request)
        assert response.status == 200

        await asyncio.sleep(1)  # wait a bit after auto ack()
        # The listeners should be executed
        assert self.mock_received_requests.get("/chat.postMessage") == 2

    @pytest.mark.asyncio
    async def test_uninstallation_and_revokes(self):
        app = AsyncApp(client=self.web_client, signing_secret=self.signing_secret)
        app._client = AsyncWebClient(token="uninstalled-revoked", base_url=self.mock_api_server_base_url)

        @app.event("app_uninstalled")
        async def handler1(say: AsyncSay):
            await say(channel="C111", text="What's up?")

        @app.event("tokens_revoked")
        async def handler2(say: AsyncSay):
            await say(channel="C111", text="What's up?")

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
        request: AsyncBoltRequest = AsyncBoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = await app.async_dispatch(request)
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
        request: AsyncBoltRequest = AsyncBoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = await app.async_dispatch(request)
        assert response.status == 200

        # AsyncApp doesn't call auth.test when booting
        assert self.mock_received_requests.get("/auth.test") is None
        await asyncio.sleep(1)  # wait a bit after auto ack()
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

    @pytest.mark.asyncio
    async def test_message_subtypes_0(self):
        app = AsyncApp(client=self.web_client, signing_secret=self.signing_secret)
        app._client = AsyncWebClient(token="uninstalled-revoked", base_url=self.mock_api_server_base_url)

        @app.event({"type": "message", "subtype": "file_share"})
        async def handler1(event):
            assert event["subtype"] == "file_share"

        timestamp, body = str(int(time())), json.dumps(self.message_file_share_body)
        request: AsyncBoltRequest = AsyncBoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = await app.async_dispatch(request)
        assert response.status == 200

    @pytest.mark.asyncio
    async def test_message_subtypes_1(self):
        app = AsyncApp(client=self.web_client, signing_secret=self.signing_secret)
        app._client = AsyncWebClient(token="uninstalled-revoked", base_url=self.mock_api_server_base_url)

        @app.event({"type": "message", "subtype": re.compile("file_.+")})
        async def handler1(event):
            assert event["subtype"] == "file_share"

        timestamp, body = str(int(time())), json.dumps(self.message_file_share_body)
        request: AsyncBoltRequest = AsyncBoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = await app.async_dispatch(request)
        assert response.status == 200

    @pytest.mark.asyncio
    async def test_message_subtypes_2(self):
        app = AsyncApp(client=self.web_client, signing_secret=self.signing_secret)
        app._client = AsyncWebClient(token="uninstalled-revoked", base_url=self.mock_api_server_base_url)

        @app.event({"type": "message", "subtype": ["file_share"]})
        async def handler1(event):
            assert event["subtype"] == "file_share"

        timestamp, body = str(int(time())), json.dumps(self.message_file_share_body)
        request: AsyncBoltRequest = AsyncBoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = await app.async_dispatch(request)
        assert response.status == 200

    @pytest.mark.asyncio
    async def test_message_subtypes_3(self):
        app = AsyncApp(client=self.web_client, signing_secret=self.signing_secret)
        app._client = AsyncWebClient(token="uninstalled-revoked", base_url=self.mock_api_server_base_url)

        @app.event("message")
        async def handler1(event):
            assert event["subtype"] == "file_share"

        timestamp, body = str(int(time())), json.dumps(self.message_file_share_body)
        request: AsyncBoltRequest = AsyncBoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = await app.async_dispatch(request)
        assert response.status == 200

    # https://github.com/slackapi/bolt-python/issues/199
    @pytest.mark.asyncio
    async def test_invalid_message_events(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )

        async def handle():
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

    @pytest.mark.asyncio
    async def test_context_generation(self):
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
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
            process_before_response=True,
        )

        @app.event("member_left_channel")
        async def handle(context: AsyncBoltContext):
            assert context.enterprise_id == "E333"
            assert context.team_id is None
            assert context.is_enterprise_install is True
            assert context.user_id == "W111"

        timestamp, json_body = str(int(time())), json.dumps(body)
        request: AsyncBoltRequest = AsyncBoltRequest(body=json_body, headers=self.build_headers(timestamp, json_body))
        response = await app.async_dispatch(request)
        assert response.status == 200

    @pytest.mark.asyncio
    async def test_additional_decorators_1(self):
        app = AsyncApp(client=self.web_client, signing_secret=self.signing_secret)

        @my_decorator
        @app.event("app_mention")
        async def handle_app_mention(say):
            await say("What's up?")

        timestamp, body = str(int(time())), json.dumps(app_mention_body)
        request: AsyncBoltRequest = AsyncBoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)
        await asyncio.sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    @pytest.mark.asyncio
    async def test_additional_decorators_2(self):
        app = AsyncApp(client=self.web_client, signing_secret=self.signing_secret)

        @app.event("app_mention")
        @my_decorator
        async def handle_app_mention(say):
            await say("What's up?")

        timestamp, body = str(int(time())), json.dumps(app_mention_body)
        request: AsyncBoltRequest = AsyncBoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)
        await asyncio.sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1


def my_decorator(f):
    @wraps(f)
    async def wrap(*args, **kwargs):
        await f(*args, **kwargs)

    return wrap


app_mention_body = {
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

reaction_added_body = {
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


async def random_sleeper(body, say, payload, event):
    assert body == app_mention_body
    assert body["event"] == payload
    assert payload == event
    seconds = random() + 2  # 2-3 seconds
    await asyncio.sleep(seconds)
    await say(f"Sending this message after sleeping for {seconds} seconds")


async def whats_up(body, say, payload, event):
    assert body["event"] == payload
    assert payload == event
    await say("What's up?")


async def skip_middleware(req, resp, next):
    # return next()
    pass


async def always_failing():
    raise Exception("Something wrong!")
