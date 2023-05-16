import pytest

from slack_bolt.request.async_request import AsyncBoltRequest


class TestAsyncRequest:
    @pytest.mark.asyncio
    async def test_all_none_values_http(self):
        req = AsyncBoltRequest(body=None, headers=None, query=None, context=None)
        assert req is not None
        assert req.raw_body == ""
        assert req.body == {}

    @pytest.mark.asyncio
    async def test_all_none_values_socket_mode(self):
        req = AsyncBoltRequest(body=None, headers=None, query=None, context=None, mode="socket_mode")
        assert req is not None
        assert req.raw_body == ""
        assert req.body == {}
