import asyncio
import pytest
from slack_sdk.signature import SignatureVerifier
from slack_sdk.web.async_client import AsyncWebClient

from slack_bolt.async_app import AsyncRespond, AsyncAck, AsyncSay
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.request.async_request import AsyncBoltRequest
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestAsyncBlockActionsRespond:
    signing_secret = "secret"
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
    async def test_success(self):
        app = AsyncApp(client=self.web_client)

        @app.event("app_mention")
        async def handle_app_mention_events(say: AsyncSay):
            await say(
                text="This is a section block with a button.",
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "This is a section block with a button.",
                        },
                        "accessory": {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Click Me"},
                            "value": "clicked",
                            "action_id": "button",
                        },
                    }
                ],
            )

        @app.action("button")
        async def handle_button_clicks(body: dict, ack: AsyncAck, respond: AsyncRespond):
            await respond(
                text="hey!",
                thread_ts=body["message"]["ts"],
                response_type="in_channel",
                replace_original=False,
            )
            await ack()

        # app_mention event
        request = AsyncBoltRequest(
            mode="socket_mode",
            body={
                "team_id": "T0G9PQBBK",
                "api_app_id": "A111",
                "event": {
                    "type": "app_mention",
                    "text": "<@U111> hey",
                    "user": "U222",
                    "ts": "1678252212.229129",
                    "blocks": [
                        {
                            "type": "rich_text",
                            "block_id": "BCCO",
                            "elements": [
                                {
                                    "type": "rich_text_section",
                                    "elements": [
                                        {"type": "user", "user_id": "U111"},
                                        {"type": "text", "text": " hey"},
                                    ],
                                }
                            ],
                        }
                    ],
                    "team": "T0G9PQBBK",
                    "channel": "C111",
                    "event_ts": "1678252212.229129",
                },
                "type": "event_callback",
                "event_id": "Ev04SPP46R6J",
                "event_time": 1678252212,
                "authorizations": [
                    {
                        "enterprise_id": None,
                        "team_id": "T0G9PQBBK",
                        "user_id": "U111",
                        "is_bot": True,
                        "is_enterprise_install": False,
                    }
                ],
                "is_ext_shared_channel": False,
                "event_context": "4-xxx",
            },
        )
        response = await app.async_dispatch(request)
        assert response.status == 200

        # block_actions request
        request = AsyncBoltRequest(
            mode="socket_mode",
            body={
                "type": "block_actions",
                "user": {"id": "U111"},
                "api_app_id": "A111",
                "container": {
                    "type": "message",
                    "message_ts": "1678252213.679169",
                    "channel_id": "C111",
                    "is_ephemeral": False,
                },
                "trigger_id": "4916855695380.xxx.yyy",
                "team": {"id": "T0G9PQBBK"},
                "enterprise": None,
                "is_enterprise_install": False,
                "channel": {"id": "C111"},
                "message": {
                    "bot_id": "B111",
                    "type": "message",
                    "text": "This is a section block with a button.",
                    "user": "U222",
                    "ts": "1678252213.679169",
                    "app_id": "A111",
                    "blocks": [
                        {
                            "type": "section",
                            "block_id": "8KR",
                            "text": {
                                "type": "mrkdwn",
                                "text": "This is a section block with a button.",
                                "verbatim": False,
                            },
                            "accessory": {
                                "type": "button",
                                "action_id": "button",
                                "text": {"type": "plain_text", "text": "Click Me"},
                                "value": "clicked",
                            },
                        }
                    ],
                    "team": "T0G9PQBBK",
                },
                "state": {"values": {}},
                "response_url": "http://localhost:8888/webhook",
                "actions": [
                    {
                        "action_id": "button",
                        "block_id": "8KR",
                        "text": {"type": "plain_text", "text": "Click Me"},
                        "value": "clicked",
                        "type": "button",
                        "action_ts": "1678252216.469172",
                    }
                ],
            },
        )
        response = await app.async_dispatch(request)
        assert response.status == 200
