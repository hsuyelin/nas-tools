import asyncio

import pytest
from slack_sdk.web.async_client import AsyncWebClient

from slack_bolt.app.async_app import AsyncApp
from slack_bolt.request.async_request import AsyncBoltRequest
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
    assert_auth_test_count_async,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestAsyncEventsIgnoreSelf:
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

    @pytest.mark.asyncio
    async def test_self_events(self):
        app = AsyncApp(client=self.web_client)
        app.event("reaction_added")(whats_up)
        request = AsyncBoltRequest(body=self_event, mode="socket_mode")
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)
        await asyncio.sleep(1)  # wait a bit after auto ack()
        # The listener should not be executed
        assert self.mock_received_requests.get("/chat.postMessage") is None

    @pytest.mark.asyncio
    async def test_self_events_response_url(self):
        app = AsyncApp(client=self.web_client)
        app.event("message")(whats_up)
        request = AsyncBoltRequest(body=response_url_message_event, mode="socket_mode")
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)
        await asyncio.sleep(1)  # wait a bit after auto ack()
        # The listener should not be executed
        assert self.mock_received_requests.get("/chat.postMessage") is None

    @pytest.mark.asyncio
    async def test_not_self_events_response_url(self):
        app = AsyncApp(client=self.web_client)
        app.event("message")(whats_up)
        request = AsyncBoltRequest(body=different_app_response_url_message_event, mode="socket_mode")
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)
        await asyncio.sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests.get("/chat.postMessage") == 1

    @pytest.mark.asyncio
    async def test_self_events_disabled(self):
        app = AsyncApp(client=self.web_client, ignoring_self_events_enabled=False)
        app.event("reaction_added")(whats_up)
        request = AsyncBoltRequest(body=self_event, mode="socket_mode")
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 0)
        await asyncio.sleep(1)  # wait a bit after auto ack()
        # The listener should be executed
        assert self.mock_received_requests.get("/chat.postMessage") == 1


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


async def whats_up(body, say, payload, event):
    assert body["event"] == payload
    assert payload == event
    await say("What's up?")
