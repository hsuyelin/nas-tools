import asyncio
import json
from time import time

import pytest
from slack_sdk.signature import SignatureVerifier
from slack_sdk.web.async_client import AsyncWebClient

from slack_bolt.app.async_app import AsyncApp
from slack_bolt.request.async_request import AsyncBoltRequest
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestAsyncMessageChanged:
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

    def build_request(self, event_payload: dict) -> AsyncBoltRequest:
        timestamp, body = str(int(time())), json.dumps(event_payload)
        return AsyncBoltRequest(body=body, headers=self.build_headers(timestamp, body))

    @pytest.mark.asyncio
    async def test_user_and_channel_id_in_context(self):
        app = AsyncApp(client=self.web_client, signing_secret=self.signing_secret, process_before_response=True)

        @app.event({"type": "message", "subtype": "message_changed"})
        async def handle_message_changed(context):
            # These should come from the main event payload part
            assert context.channel_id == "C111"
            assert context.user_id == "U111"
            # The following ones come from authorizations[0]
            assert context.team_id == "T-auth"
            assert context.enterprise_id == "E-auth"

        request = self.build_request(event_payload)
        response = await app.async_dispatch(request)
        assert response.status == 200


event_payload = {
    "token": "verification-token",
    "team_id": "T111",
    "enterprise_id": "E111",
    "api_app_id": "A111",
    "event": {
        "type": "message",
        "subtype": "message_changed",
        "message": {
            "type": "message",
            "text": "updated message",
            "user": "U111",
            "team": "T111",
            "edited": {"user": "U111", "ts": "1665102362.000000"},
            "blocks": [
                {
                    "type": "rich_text",
                    "block_id": "xwvU3",
                    "elements": [{"type": "rich_text_section", "elements": [{"type": "text", "text": "updated message"}]}],
                }
            ],
        },
        "previous_message": {
            "type": "message",
            "text": "original message",
            "user": "U222",
            "team": "T111",
            "ts": "1665102338.901939",
            "blocks": [
                {
                    "type": "rich_text",
                    "block_id": "URf",
                    "elements": [{"type": "rich_text_section", "elements": [{"type": "text", "text": "original message"}]}],
                }
            ],
        },
        "channel": "C111",
        "hidden": True,
        "ts": "1665102362.013600",
        "event_ts": "1665102362.013600",
        "channel_type": "channel",
    },
    "type": "event_callback",
    "event_id": "Ev111",
    "event_time": 1665102362,
    "authorizations": [
        {
            "enterprise_id": "E-auth",
            "team_id": "T-auth",
            "user_id": "U-auth",
            "is_bot": True,
            "is_enterprise_install": False,
        }
    ],
    "is_ext_shared_channel": False,
    "event_context": "1-message-T111-C111",
}
