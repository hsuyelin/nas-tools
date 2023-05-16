import asyncio
import json
import re
from time import time

import pytest
from slack_sdk.signature import SignatureVerifier
from slack_sdk.web.async_client import AsyncWebClient

from slack_bolt import BoltResponse
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.request.async_request import AsyncBoltRequest
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
    assert_auth_test_count_async,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestAsyncMessage:
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

    def build_request_from_body(self, message_body: dict) -> AsyncBoltRequest:
        timestamp, body = str(int(time())), json.dumps(message_body)
        return AsyncBoltRequest(body=body, headers=self.build_headers(timestamp, body))

    def build_request(self) -> AsyncBoltRequest:
        return self.build_request_from_body(message_body)

    def build_request2(self) -> AsyncBoltRequest:
        return self.build_request_from_body(message_body2)

    def build_request3(self) -> AsyncBoltRequest:
        return self.build_request_from_body(message_body3)

    @pytest.mark.asyncio
    async def test_string_keyword(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.message("Hello")(whats_up)

        request = self.build_request()
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)
        await asyncio.sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    @pytest.mark.asyncio
    async def test_all_message_matching_1(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )

        @app.message("")
        async def handle_all_new_messages(say):
            await say("Thanks!")

        request = self.build_request2()
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)
        await asyncio.sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    @pytest.mark.asyncio
    async def test_all_message_matching_2(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )

        @app.message()
        async def handle_all_new_messages(say):
            await say("Thanks!")

        request = self.build_request2()
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)
        await asyncio.sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    @pytest.mark.asyncio
    async def test_string_keyword_capturing(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.message("We've received ([0-9]+) messages from (.+)!")(verify_matches)

        request = self.build_request2()
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)
        await asyncio.sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    @pytest.mark.asyncio
    async def test_string_keyword_capturing2(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.message(re.compile("We've received ([0-9]+) messages from (.+)!"))(verify_matches)

        request = self.build_request2()
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)
        await asyncio.sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    @pytest.mark.asyncio
    async def test_string_keyword_capturing_multi_capture(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.message(re.compile("([a-z|A-Z]{3,}-[0-9]+)"))(verify_matches_multi)

        request = self.build_request3()
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)
        await asyncio.sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    @pytest.mark.asyncio
    async def test_string_keyword_unmatched(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.message("HELLO")(whats_up)

        request = self.build_request()
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_regexp_keyword(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.message(re.compile("He.lo"))(whats_up)

        request = self.build_request()
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)
        await asyncio.sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    @pytest.mark.asyncio
    async def test_regexp_keyword_unmatched(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.message(re.compile("HELLO"))(whats_up)

        request = self.build_request()
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

    # https://github.com/slackapi/bolt-python/issues/232
    @pytest.mark.asyncio
    async def test_issue_232_message_listener_middleware(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )

        called = {
            "first": False,
            "second": False,
        }

        async def this_should_be_skipped():
            return BoltResponse(status=500, body="failed")

        @app.message("first", middleware=[this_should_be_skipped])
        async def first():
            called["first"] = True

        @app.message("second", middleware=[])
        async def second():
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
        response = await app.async_dispatch(request)
        assert response.status == 200

        await asyncio.sleep(0.3)
        assert called["first"] is False
        assert called["second"] is True

    @pytest.mark.asyncio
    async def test_issue_561_matchers(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )

        async def just_fail():
            raise "This matcher should not be called!"

        @app.message("xxx", matchers=[just_fail])
        async def just_ack():
            raise "This listener should not be called!"

        request = self.build_request()
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)


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


async def whats_up(body, say):
    assert body == message_body
    await say("What's up?")


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


async def verify_matches(context, say):
    assert context["matches"] == ("103", "you")
    assert context.matches == ("103", "you")
    await say("Thanks!")


async def verify_matches_multi(context, say, body, payload, message):
    assert context["matches"] == ("JIRA-1234", "SCM-567", "BUG-169")
    assert context.matches == ("JIRA-1234", "SCM-567", "BUG-169")
    await say("Thanks!")
