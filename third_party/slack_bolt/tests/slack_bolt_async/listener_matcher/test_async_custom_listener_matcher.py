import pytest

from slack_bolt.listener_matcher.async_listener_matcher import (
    AsyncCustomListenerMatcher,
    AsyncListenerMatcher,
)
from slack_bolt.request.async_request import AsyncBoltRequest
from slack_bolt.response import BoltResponse


async def func(body, request, response, dummy):
    assert body is not None
    assert request is not None
    assert response is not None
    assert dummy is None
    return body["result"]


class TestAsyncCustomListenerMatcher:
    @pytest.mark.asyncio
    async def test_instantiation(self):
        matcher: AsyncListenerMatcher = AsyncCustomListenerMatcher(
            app_name="foo",
            func=func,
        )
        resp = BoltResponse(status=201)

        req = AsyncBoltRequest(body='payload={"result":true}')
        result = await matcher.async_matches(req, resp)
        assert result is True

        req = AsyncBoltRequest(body='payload={"result":false}')
        result = await matcher.async_matches(req, resp)
        assert result is False
