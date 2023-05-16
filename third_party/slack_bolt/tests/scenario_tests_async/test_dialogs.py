import asyncio
import json
from time import time
from urllib.parse import quote

import pytest
from slack_sdk.signature import SignatureVerifier
from slack_sdk.web.async_client import AsyncWebClient

from slack_bolt.app.async_app import AsyncApp
from slack_bolt.request.async_request import AsyncBoltRequest
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
    assert_auth_test_count_async,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestAsyncAttachmentActions:
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
            "content-type": ["application/x-www-form-urlencoded"],
            "x-slack-signature": [self.generate_signature(body, timestamp)],
            "x-slack-request-timestamp": [timestamp],
        }

    def build_valid_request(self, body) -> AsyncBoltRequest:
        timestamp = str(int(time()))
        return AsyncBoltRequest(body=body, headers=self.build_headers(timestamp, body))

    @pytest.mark.asyncio
    async def test_mock_server_is_running(self):
        resp = await self.web_client.api_test()
        assert resp != None

    @pytest.mark.asyncio
    async def test_success_without_type(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.options("dialog-callback-id")(handle_suggestion)
        app.action("dialog-callback-id")(handle_submission_or_cancellation)

        request = self.build_valid_request(suggestion_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 200
        assert response.body != ""
        assert response.headers["content-type"][0] == "application/json;charset=utf-8"
        await assert_auth_test_count_async(self, 1)

        request = self.build_valid_request(submission_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 200
        assert response.body == ""
        await assert_auth_test_count_async(self, 1)

        request = self.build_valid_request(cancellation_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 200
        assert response.body == ""
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_success(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.options({"type": "dialog_suggestion", "callback_id": "dialog-callback-id"})(handle_suggestion)
        app.action({"type": "dialog_submission", "callback_id": "dialog-callback-id"})(handle_submission)
        app.action({"type": "dialog_cancellation", "callback_id": "dialog-callback-id"})(handle_cancellation)

        request = self.build_valid_request(suggestion_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 200
        assert response.body != ""
        assert response.headers["content-type"][0] == "application/json;charset=utf-8"
        await assert_auth_test_count_async(self, 1)

        request = self.build_valid_request(submission_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 200
        assert response.body == ""
        await assert_auth_test_count_async(self, 1)

        request = self.build_valid_request(cancellation_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 200
        assert response.body == ""
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_success_2(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.dialog_suggestion("dialog-callback-id")(handle_suggestion)
        app.dialog_submission("dialog-callback-id")(handle_submission)
        app.dialog_cancellation("dialog-callback-id")(handle_cancellation)

        request = self.build_valid_request(suggestion_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 200
        assert response.body != ""
        assert response.headers["content-type"][0] == "application/json;charset=utf-8"
        await assert_auth_test_count_async(self, 1)

        request = self.build_valid_request(submission_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 200
        assert response.body == ""
        await assert_auth_test_count_async(self, 1)

        request = self.build_valid_request(cancellation_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 200
        assert response.body == ""
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_process_before_response(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
            process_before_response=True,
        )
        app.options({"type": "dialog_suggestion", "callback_id": "dialog-callback-id"})(handle_suggestion)
        app.action({"type": "dialog_submission", "callback_id": "dialog-callback-id"})(handle_submission)
        app.action({"type": "dialog_cancellation", "callback_id": "dialog-callback-id"})(handle_cancellation)

        request = self.build_valid_request(suggestion_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 200
        assert response.body != ""
        assert response.headers["content-type"][0] == "application/json;charset=utf-8"
        await assert_auth_test_count_async(self, 1)

        request = self.build_valid_request(submission_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 200
        assert response.body == ""
        await assert_auth_test_count_async(self, 1)

        request = self.build_valid_request(cancellation_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 200
        assert response.body == ""
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_process_before_response_2(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
            process_before_response=True,
        )
        app.dialog_suggestion("dialog-callback-id")(handle_suggestion)
        app.dialog_submission("dialog-callback-id")(handle_submission)
        app.dialog_cancellation("dialog-callback-id")(handle_cancellation)

        request = self.build_valid_request(suggestion_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 200
        assert response.body == json.dumps(options_response)
        assert response.headers["content-type"][0] == "application/json;charset=utf-8"
        await assert_auth_test_count_async(self, 1)

        request = self.build_valid_request(submission_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 200
        assert response.body == ""
        await assert_auth_test_count_async(self, 1)

        request = self.build_valid_request(cancellation_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 200
        assert response.body == ""
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_suggestion_failure_without_type(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        request = self.build_valid_request(suggestion_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

        app.options("dialog-callback-iddddd")(handle_suggestion)
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_suggestion_failure(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        request = self.build_valid_request(suggestion_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

        app.dialog_suggestion("dialog-callback-iddddd")(handle_suggestion)
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_suggestion_failure_2(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        request = self.build_valid_request(suggestion_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

        app.options({"type": "dialog_suggestion", "callback_id": "dialog-callback-iddddd"})(handle_suggestion)
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_submission_failure_without_type(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        request = self.build_valid_request(suggestion_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

        app.action("dialog-callback-iddddd")(handle_submission)
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_submission_failure(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        request = self.build_valid_request(suggestion_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

        app.dialog_submission("dialog-callback-iddddd")(handle_submission)
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_submission_failure_2(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        request = self.build_valid_request(suggestion_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

        app.action({"type": "dialog_submission", "callback_id": "dialog-callback-iddddd"})(handle_submission)
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_cancellation_failure_without_type(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        request = self.build_valid_request(suggestion_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

        app.action("dialog-callback-iddddd")(handle_cancellation)
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_cancellation_failure(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        request = self.build_valid_request(suggestion_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

        app.dialog_cancellation("dialog-callback-iddddd")(handle_cancellation)
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_cancellation_failure_2(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        request = self.build_valid_request(suggestion_raw_body)
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)

        app.action({"type": "dialog_cancellation", "callback_id": "dialog-callback-iddddd"})(handle_cancellation)
        response = await app.async_dispatch(request)
        assert response.status == 404
        await assert_auth_test_count_async(self, 1)


suggestion_body = {
    "type": "dialog_suggestion",
    "token": "verification_token",
    "action_ts": "1596603332.676855",
    "team": {
        "id": "T111",
        "domain": "workspace-domain",
        "enterprise_id": "E111",
        "enterprise_name": "Sandbox Org",
    },
    "user": {"id": "W111", "name": "primary-owner", "team_id": "T111"},
    "channel": {"id": "C111", "name": "test-channel"},
    "name": "types",
    "value": "search keyword",
    "callback_id": "dialog-callback-id",
    "state": "Limo",
}

submission_body = {
    "type": "dialog_submission",
    "token": "verification_token",
    "action_ts": "1596603334.328193",
    "team": {
        "id": "T111",
        "domain": "workspace-domain",
        "enterprise_id": "E111",
        "enterprise_name": "Sandbox Org",
    },
    "user": {"id": "W111", "name": "primary-owner", "team_id": "T111"},
    "channel": {"id": "C111", "name": "test-channel"},
    "submission": {
        "loc_origin": "Tokyo",
        "loc_destination": "Osaka",
        "types": "FE-459",
    },
    "callback_id": "dialog-callback-id",
    "response_url": "https://hooks.slack.com/app/T111/111/xxx",
    "state": "Limo",
}

cancellation_body = {
    "type": "dialog_cancellation",
    "token": "verification_token",
    "action_ts": "1596603453.047897",
    "team": {
        "id": "T111",
        "domain": "workspace-domain",
        "enterprise_id": "E111",
        "enterprise_name": "Sandbox Org",
    },
    "user": {"id": "W111", "name": "primary-owner", "team_id": "T111"},
    "channel": {"id": "C111", "name": "test-channel"},
    "callback_id": "dialog-callback-id",
    "response_url": "https://hooks.slack.com/app/T111/111/xxx",
    "state": "Limo",
}

suggestion_raw_body = f"payload={quote(json.dumps(suggestion_body))}"
submission_raw_body = f"payload={quote(json.dumps(submission_body))}"
cancellation_raw_body = f"payload={quote(json.dumps(cancellation_body))}"


async def handle_submission(ack):
    await ack()


options_response = {
    "options": [
        {
            "label": "[UXD-342] The button color should be artichoke green, not jalapeño",
            "value": "UXD-342",
        },
        {"label": "[FE-459] Remove the marquee tag", "value": "FE-459"},
        {
            "label": "[FE-238] Too many shades of gray in master CSS",
            "value": "FE-238",
        },
    ]
}


async def handle_suggestion(ack, body, payload, options):
    assert body == options
    assert payload == options
    await ack(options_response)


async def handle_cancellation(ack, body, payload, action):
    assert body == action
    assert payload == action
    await ack()


async def handle_submission_or_cancellation(ack, body, payload, action):
    assert body == action
    assert payload == action
    await ack()
