import asyncio

import pytest
from slack_sdk.web.async_client import AsyncWebClient

from slack_bolt.middleware.authorization.async_single_team_authorization import (
    AsyncSingleTeamAuthorization,
)
from slack_bolt.middleware.authorization.internals import _build_error_text
from slack_bolt.request.async_request import AsyncBoltRequest
from slack_bolt.response import BoltResponse
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


async def next():
    return BoltResponse(status=200)


class TestSingleTeamAuthorization:
    mock_api_server_base_url = "http://localhost:8888"

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
    async def test_success_pattern(self):
        authorization = AsyncSingleTeamAuthorization()
        req = AsyncBoltRequest(body="payload={}", headers={})
        req.context["client"] = AsyncWebClient(base_url=self.mock_api_server_base_url, token="xoxb-valid")
        resp = BoltResponse(status=404)

        resp = await authorization.async_process(req=req, resp=resp, next=next)

        assert resp.status == 200
        assert resp.body == ""

    @pytest.mark.asyncio
    async def test_failure_pattern(self):
        authorization = AsyncSingleTeamAuthorization()
        req = AsyncBoltRequest(body="payload={}", headers={})
        req.context["client"] = AsyncWebClient(base_url=self.mock_api_server_base_url, token="dummy")
        resp = BoltResponse(status=404)

        resp = await authorization.async_process(req=req, resp=resp, next=next)

        assert resp.status == 200
        assert resp.body == _build_error_text()
