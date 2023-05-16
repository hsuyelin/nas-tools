import asyncio

import pytest
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.web.async_slack_response import AsyncSlackResponse

from slack_bolt.context.say.async_say import AsyncSay
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)


class TestAsyncSay:
    @pytest.fixture
    def event_loop(self):
        setup_mock_web_api_server(self)
        valid_token = "xoxb-valid"
        mock_api_server_base_url = "http://localhost:8888"
        self.web_client = AsyncWebClient(token=valid_token, base_url=mock_api_server_base_url)

        loop = asyncio.get_event_loop()
        yield loop
        loop.close()
        cleanup_mock_web_api_server(self)

    @pytest.mark.asyncio
    async def test_say(self):
        say = AsyncSay(client=self.web_client, channel="C111")
        response: AsyncSlackResponse = await say(text="Hi there!")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_say_unfurl_options(self):
        say = AsyncSay(client=self.web_client, channel="C111")
        response: AsyncSlackResponse = await say(text="Hi there!", unfurl_links=True, unfurl_media=True)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_say_reply_in_thread(self):
        say = AsyncSay(client=self.web_client, channel="C111")
        response: AsyncSlackResponse = await say(text="Hi there!", thread_ts="111.222", reply_broadcast=True)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_say_dict(self):
        say = AsyncSay(client=self.web_client, channel="C111")
        response: AsyncSlackResponse = await say({"text": "Hi!"})
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_say_dict_channel(self):
        say = AsyncSay(client=self.web_client, channel="C111")
        response: AsyncSlackResponse = await say({"text": "Hi!", "channel": "C111"})
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_say_invalid(self):
        say = AsyncSay(client=self.web_client, channel="C111")
        with pytest.raises(ValueError):
            await say([])

    @pytest.mark.asyncio
    async def test_say_shared_dict_as_arg(self):
        # this shared dict object must not be modified by say method
        shared_template_dict = {"text": "Hi there!"}
        say = AsyncSay(client=self.web_client, channel="C111")
        response: AsyncSlackResponse = await say(shared_template_dict)
        assert response.status_code == 200
        assert shared_template_dict.get("channel") is None

        say = AsyncSay(client=self.web_client, channel="C222")
        response: AsyncSlackResponse = await say(shared_template_dict)
        assert response.status_code == 200
        assert shared_template_dict.get("channel") is None
