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
    assert_auth_test_count_async,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestAsyncMessageFileShare:
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

    def build_request(self, payload: dict) -> AsyncBoltRequest:
        timestamp, body = str(int(time())), json.dumps(payload)
        return AsyncBoltRequest(body=body, headers=self.build_headers(timestamp, body))

    @pytest.mark.asyncio
    async def test_string_keyword(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        result = {"call_count": 0}

        @app.message("Hi there!")
        async def handle_messages(event, logger):
            logger.info(event)
            result["call_count"] = result["call_count"] + 1

        request = self.build_request(event_payload)
        response = await app.async_dispatch(request)
        assert response.status == 200

        request = self.build_request(event_payload)
        response = await app.async_dispatch(request)
        assert response.status == 200

        await assert_auth_test_count_async(self, 1)
        await asyncio.sleep(1)  # wait a bit after auto ack()
        assert result["call_count"] == 2


event_payload = {
    "token": "xxx",
    "team_id": "T111",
    "api_app_id": "A111",
    "event": {
        "type": "message",
        "text": "Hi there!",
        "files": [
            {
                "id": "F111",
                "created": 1652227642,
                "timestamp": 1652227642,
                "name": "file.png",
                "title": "file.png",
                "mimetype": "image/png",
                "filetype": "png",
                "pretty_type": "PNG",
                "user": "U111",
                "editable": False,
                "size": 92582,
                "mode": "hosted",
                "is_external": False,
                "external_type": "",
                "is_public": True,
                "public_url_shared": False,
                "display_as_bot": False,
                "username": "",
                "url_private": "https://files.slack.com/files-pri/T111-F111/file.png",
                "url_private_download": "https://files.slack.com/files-pri/T111-F111/download/file.png",
                "media_display_type": "unknown",
                "thumb_64": "https://files.slack.com/files-tmb/T111-F111-f820f29515/file_64.png",
                "thumb_80": "https://files.slack.com/files-tmb/T111-F111-f820f29515/file_80.png",
                "thumb_360": "https://files.slack.com/files-tmb/T111-F111-f820f29515/file_360.png",
                "thumb_360_w": 360,
                "thumb_360_h": 115,
                "thumb_480": "https://files.slack.com/files-tmb/T111-F111-f820f29515/file_480.png",
                "thumb_480_w": 480,
                "thumb_480_h": 153,
                "thumb_160": "https://files.slack.com/files-tmb/T111-F111-f820f29515/file_160.png",
                "thumb_720": "https://files.slack.com/files-tmb/T111-F111-f820f29515/file_720.png",
                "thumb_720_w": 720,
                "thumb_720_h": 230,
                "thumb_800": "https://files.slack.com/files-tmb/T111-F111-f820f29515/file_800.png",
                "thumb_800_w": 800,
                "thumb_800_h": 255,
                "thumb_960": "https://files.slack.com/files-tmb/T111-F111-f820f29515/file_960.png",
                "thumb_960_w": 960,
                "thumb_960_h": 306,
                "thumb_1024": "https://files.slack.com/files-tmb/T111-F111-f820f29515/file_1024.png",
                "thumb_1024_w": 1024,
                "thumb_1024_h": 327,
                "original_w": 1134,
                "original_h": 362,
                "thumb_tiny": "AwAPADCkCAOcUEj0zTaKAHZHpT9oxwR+VRVMBQA0r3yPypu0f3v0p5yBTCcmmI//2Q==",
                "permalink": "https://xxx.slack.com/files/U111/F111/file.png",
                "permalink_public": "https://slack-files.com/T111-F111-faecabecf7",
                "has_rich_preview": False,
            }
        ],
        "upload": False,
        "user": "U111",
        "display_as_bot": False,
        "ts": "1652227646.593159",
        "blocks": [
            {
                "type": "rich_text",
                "block_id": "ba4",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [{"type": "text", "text": "Hi there!"}],
                    }
                ],
            }
        ],
        "client_msg_id": "ca088267-717f-41a8-9db8-c98ae14ad6a0",
        "channel": "C111",
        "subtype": "file_share",
        "event_ts": "1652227646.593159",
        "channel_type": "channel",
    },
    "type": "event_callback",
    "event_id": "Ev03EGJQAVMM",
    "event_time": 1652227646,
    "authorizations": [
        {
            "enterprise_id": None,
            "team_id": "T111",
            "user_id": "U222",
            "is_bot": True,
            "is_enterprise_install": False,
        }
    ],
    "is_ext_shared_channel": False,
    "event_context": "4-xxx",
}
