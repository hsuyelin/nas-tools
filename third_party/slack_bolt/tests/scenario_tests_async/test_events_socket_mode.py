import asyncio
from random import random

import pytest
from slack_sdk.web.async_client import AsyncWebClient

from slack_bolt.app.async_app import AsyncApp
from slack_bolt.context.say.async_say import AsyncSay
from slack_bolt.request.async_request import AsyncBoltRequest
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
    assert_auth_test_count_async,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestAsyncEvents:
    valid_token = "xoxb-valid"
    mock_api_server_base_url = "http://localhost:8888"
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

    def build_valid_app_mention_request(self) -> AsyncBoltRequest:
        return AsyncBoltRequest(body=app_mention_body, mode="socket_mode")

    @pytest.mark.asyncio
    async def test_mock_server_is_running(self):
        resp = await self.web_client.api_test()
        assert resp != None

    @pytest.mark.asyncio
    async def test_app_mention(self):
        app = AsyncApp(client=self.web_client)
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
        app = AsyncApp(client=self.web_client)
        app.event("app_mention", middleware=[skip_middleware])(whats_up)

        request = self.build_valid_app_mention_request()
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_simultaneous_requests(self):
        app = AsyncApp(client=self.web_client)
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
        return AsyncBoltRequest(body=reaction_added_body, mode="socket_mode")

    @pytest.mark.asyncio
    async def test_reaction_added(self):
        app = AsyncApp(client=self.web_client)
        app.event("reaction_added")(whats_up)

        request = self.build_valid_reaction_added_request()
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)
        await asyncio.sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    @pytest.mark.asyncio
    async def test_stable_auto_ack(self):
        app = AsyncApp(client=self.web_client)
        app.event("reaction_added")(always_failing)

        for _ in range(10):
            request = self.build_valid_reaction_added_request()
            response = await app.async_dispatch(request)
            assert response.status == 200

    @pytest.mark.asyncio
    async def test_self_events(self):
        app = AsyncApp(client=self.web_client)
        app.event("reaction_added")(whats_up)

        self_event = {
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
        request = AsyncBoltRequest(body=self_event, mode="socket_mode")
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)
        await asyncio.sleep(1)  # wait a bit after auto ack()
        # The listener should not be executed
        assert self.mock_received_requests.get("/chat.postMessage") is None

    @pytest.mark.asyncio
    async def test_self_joined_left_events(self):
        app = AsyncApp(client=self.web_client)
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

        request = AsyncBoltRequest(body=join_event_body, mode="socket_mode")
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)

        request = AsyncBoltRequest(body=left_event_body, mode="socket_mode")
        response = await app.async_dispatch(request)
        assert response.status == 200

        await asyncio.sleep(1)  # wait a bit after auto ack()
        # The listeners should be executed
        assert self.mock_received_requests.get("/chat.postMessage") == 2

    @pytest.mark.asyncio
    async def test_joined_left_events(self):
        app = AsyncApp(client=self.web_client)
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

        request = AsyncBoltRequest(body=join_event_body, mode="socket_mode")
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)

        request = AsyncBoltRequest(body=left_event_body, mode="socket_mode")
        response = await app.async_dispatch(request)
        assert response.status == 200

        await asyncio.sleep(1)  # wait a bit after auto ack()
        # The listeners should be executed
        assert self.mock_received_requests.get("/chat.postMessage") == 2

    @pytest.mark.asyncio
    async def test_uninstallation_and_revokes(self):
        app = AsyncApp(client=self.web_client)
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

        request: AsyncBoltRequest = AsyncBoltRequest(body=app_uninstalled_body, mode="socket_mode")
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

        request: AsyncBoltRequest = AsyncBoltRequest(body=tokens_revoked_body, mode="socket_mode")
        response = await app.async_dispatch(request)
        assert response.status == 200

        # AsyncApp doesn't call auth.test when booting
        assert self.mock_received_requests.get("/auth.test") is None
        await asyncio.sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 2


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
