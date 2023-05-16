import logging
import pytest

from slack_bolt.request.async_request import AsyncBoltRequest
from slack_bolt.listener.async_listener_completion_handler import (
    AsyncCustomListenerCompletionHandler,
)


class TestAsyncListenerCompletionHandler:
    @pytest.mark.asyncio
    async def test_handler(self):
        result = {"called": False}

        async def f():
            result["called"] = True

        handler = AsyncCustomListenerCompletionHandler(
            logger=logging.getLogger(__name__),
            func=f,
        )
        request = AsyncBoltRequest(
            body="{}",
            query={},
            headers={"content-type": ["application/json"]},
            context={},
        )
        await handler.handle(request, None)
        assert result["called"] is True
