import asyncio
import inspect
import json
from time import time
from typing import Callable

import pytest
from slack_sdk.signature import SignatureVerifier
from slack_sdk.web.async_client import AsyncWebClient

from slack_bolt.context.async_context import AsyncBoltContext
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.context.ack.async_ack import AsyncAck
from slack_bolt.context.say.async_say import AsyncSay
from slack_bolt.request.async_request import AsyncBoltRequest
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
    assert_auth_test_count_async,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestAppUsingMethodsInClass:
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

    def test_inspect_behaviors(self):
        async def f():
            pass

        assert inspect.ismethod(f) is False

        class A:
            async def b(self):
                pass

            @classmethod
            async def c(cls):
                pass

            @staticmethod
            async def d():
                pass

        a = A()
        assert inspect.ismethod(a.b) is True
        assert inspect.ismethod(A.c) is True
        assert inspect.ismethod(A.d) is False

    async def run_app_and_verify(self, app: AsyncApp):
        payload = {
            "type": "message_action",
            "token": "verification_token",
            "action_ts": "1583637157.207593",
            "team": {
                "id": "T111",
                "domain": "test-test",
                "enterprise_id": "E111",
                "enterprise_name": "Org Name",
            },
            "user": {"id": "W111", "name": "test-test"},
            "channel": {"id": "C111", "name": "dev"},
            "callback_id": "test-shortcut",
            "trigger_id": "111.222.xxx",
            "message_ts": "1583636382.000300",
            "message": {
                "client_msg_id": "zzzz-111-222-xxx-yyy",
                "type": "message",
                "text": "<@W222> test",
                "user": "W111",
                "ts": "1583636382.000300",
                "team": "T111",
                "blocks": [
                    {
                        "type": "rich_text",
                        "block_id": "d7eJ",
                        "elements": [
                            {
                                "type": "rich_text_section",
                                "elements": [
                                    {"type": "user", "user_id": "U222"},
                                    {"type": "text", "text": " test"},
                                ],
                            }
                        ],
                    }
                ],
            },
            "response_url": "https://hooks.slack.com/app/T111/111/xxx",
        }

        timestamp, body = str(int(time())), f"payload={json.dumps(payload)}"
        request: AsyncBoltRequest = AsyncBoltRequest(
            body=body,
            headers={
                "content-type": ["application/x-www-form-urlencoded"],
                "x-slack-signature": [
                    self.signature_verifier.generate_signature(
                        body=body,
                        timestamp=timestamp,
                    )
                ],
                "x-slack-request-timestamp": [timestamp],
            },
        )
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)
        await asyncio.sleep(0.5)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    @pytest.mark.asyncio
    async def test_class_methods(self):
        app = AsyncApp(client=self.web_client, signing_secret=self.signing_secret)
        app.use(AwesomeClass.class_middleware)
        app.shortcut("test-shortcut")(AwesomeClass.class_method)
        await self.run_app_and_verify(app)

    @pytest.mark.asyncio
    async def test_class_methods_uncommon_name(self):
        app = AsyncApp(client=self.web_client, signing_secret=self.signing_secret)
        app.use(AwesomeClass.class_middleware)
        app.shortcut("test-shortcut")(AwesomeClass.class_method2)
        await self.run_app_and_verify(app)

    @pytest.mark.asyncio
    async def test_instance_methods(self):
        app = AsyncApp(client=self.web_client, signing_secret=self.signing_secret)
        awesome = AwesomeClass("Slackbot")
        app.use(awesome.instance_middleware)
        app.shortcut("test-shortcut")(awesome.instance_method)
        await self.run_app_and_verify(app)

    @pytest.mark.asyncio
    async def test_instance_methods_uncommon_name_1(self):
        app = AsyncApp(client=self.web_client, signing_secret=self.signing_secret)
        awesome = AwesomeClass("Slackbot")
        app.use(awesome.instance_middleware)
        app.shortcut("test-shortcut")(awesome.instance_method2)
        await self.run_app_and_verify(app)

    @pytest.mark.asyncio
    async def test_instance_methods_uncommon_name_2(self):
        app = AsyncApp(client=self.web_client, signing_secret=self.signing_secret)
        awesome = AwesomeClass("Slackbot")
        app.use(awesome.instance_middleware)
        app.shortcut("test-shortcut")(awesome.instance_method3)
        await self.run_app_and_verify(app)

    @pytest.mark.asyncio
    async def test_static_methods(self):
        app = AsyncApp(client=self.web_client, signing_secret=self.signing_secret)
        app.use(AwesomeClass.static_middleware)
        app.shortcut("test-shortcut")(AwesomeClass.static_method)
        await self.run_app_and_verify(app)

    @pytest.mark.asyncio
    async def test_invalid_arg_in_func(self):
        app = AsyncApp(client=self.web_client, signing_secret=self.signing_secret)
        app.shortcut("test-shortcut")(top_level_function)
        await self.run_app_and_verify(app)


class AwesomeClass:
    def __init__(self, name: str):
        self.name = name

    @classmethod
    async def class_middleware(cls, next: Callable):
        await next()

    async def instance_middleware(self, next: Callable):
        await next()

    @staticmethod
    async def static_middleware(next):
        await next()

    @classmethod
    async def class_method(cls, context: AsyncBoltContext, say: AsyncSay, ack: AsyncAck):
        await ack()
        await say(f"Hello <@{context.user_id}>!")

    @classmethod
    async def class_method2(xyz, context: AsyncBoltContext, say: AsyncSay, ack: AsyncAck):
        await ack()
        await say(f"Hello <@{context.user_id}>!")

    async def instance_method(self, context: AsyncBoltContext, say: AsyncSay, ack: AsyncAck):
        await ack()
        await say(f"Hello <@{context.user_id}>! My name is {self.name}")

    async def instance_method2(whatever, context: AsyncBoltContext, say: AsyncSay, ack: AsyncAck):
        await ack()
        await say(f"Hello <@{context.user_id}>! My name is {whatever.name}")

    text = "hello world"

    async def instance_method3(this, ack, logger, say):
        await ack()
        logger.debug(this.text)
        await say(f"Hi there!")

    @staticmethod
    async def static_method(context: AsyncBoltContext, say: AsyncSay, ack: AsyncAck):
        await ack()
        await say(f"Hello <@{context.user_id}>!")


async def top_level_function(invalid_arg, ack, say):
    assert invalid_arg is None
    await ack()
    await say("Hi")
