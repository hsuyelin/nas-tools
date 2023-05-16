import asyncio

import pytest
from slack_sdk.web.async_client import AsyncWebClient

from slack_bolt import BoltResponse
from slack_bolt.oauth.async_callback_options import (
    AsyncFailureArgs,
    AsyncSuccessArgs,
    AsyncCallbackOptions,
)
from slack_bolt.oauth.async_oauth_flow import AsyncOAuthFlow
from slack_bolt.request.async_request import AsyncBoltRequest
from tests.mock_web_api_server import (
    cleanup_mock_web_api_server,
    setup_mock_web_api_server,
)


class TestAsyncOAuthFlowSQLite3:
    mock_api_server_base_url = "http://localhost:8888"

    @pytest.fixture
    def event_loop(self):
        setup_mock_web_api_server(self)
        loop = asyncio.get_event_loop()
        yield loop
        loop.close()
        cleanup_mock_web_api_server(self)

    def next(self):
        pass

    @pytest.mark.asyncio
    async def test_instantiation(self):
        oauth_flow = AsyncOAuthFlow.sqlite3(
            database="./logs/test_db",
            client_id="111.222",
            client_secret="xxx",
            scopes=["chat:write", "commands"],
        )
        assert oauth_flow is not None
        assert oauth_flow.logger is not None
        assert oauth_flow.client is not None

    @pytest.mark.asyncio
    async def test_handle_installation(self):
        oauth_flow = AsyncOAuthFlow.sqlite3(
            database="./logs/test_db",
            client_id="111.222",
            client_secret="xxx",
            scopes=["chat:write", "commands"],
        )
        req = AsyncBoltRequest(body="")
        resp = await oauth_flow.handle_installation(req)
        assert resp.status == 200
        assert resp.headers.get("content-type") == ["text/html; charset=utf-8"]
        assert "https://slack.com/oauth/v2/authorize?state=" in resp.body

    @pytest.mark.asyncio
    async def test_handle_callback(self):
        oauth_flow = AsyncOAuthFlow.sqlite3(
            database="./logs/test_db",
            client=AsyncWebClient(base_url=self.mock_api_server_base_url),
            client_id="111.222",
            client_secret="xxx",
            scopes=["chat:write", "commands"],
            success_url="https://www.example.com/completion",
            failure_url="https://www.example.com/failure",
        )
        state = await oauth_flow.issue_new_state(None)
        req = AsyncBoltRequest(
            body="",
            query=f"code=foo&state={state}",
            headers={"cookie": [f"{oauth_flow.settings.state_cookie_name}={state}"]},
        )
        resp = await oauth_flow.handle_callback(req)
        assert resp.status == 200
        assert "https://www.example.com/completion" in resp.body

    @pytest.mark.asyncio
    async def test_handle_callback_invalid_state(self):
        oauth_flow = AsyncOAuthFlow.sqlite3(
            database="./logs/test_db",
            client_id="111.222",
            client_secret="xxx",
            scopes=["chat:write", "commands"],
        )
        state = await oauth_flow.issue_new_state(None)
        req = AsyncBoltRequest(
            body="",
            query=f"code=foo&state=invalid",
            headers={"cookie": [f"{oauth_flow.settings.state_cookie_name}={state}"]},
        )
        resp = await oauth_flow.handle_callback(req)
        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_handle_callback_using_options(self):
        async def success(args: AsyncSuccessArgs) -> BoltResponse:
            assert args.request is not None
            return BoltResponse(status=200, body="customized")

        async def failure(args: AsyncFailureArgs) -> BoltResponse:
            assert args.request is not None
            assert args.reason is not None
            return BoltResponse(status=502, body="customized")

        oauth_flow = AsyncOAuthFlow.sqlite3(
            client=AsyncWebClient(base_url=self.mock_api_server_base_url),
            database="./logs/test_db",
            client_id="111.222",
            client_secret="xxx",
            scopes=["chat:write", "commands"],
            callback_options=AsyncCallbackOptions(
                success=success,
                failure=failure,
            ),
        )
        state = await oauth_flow.issue_new_state(None)
        req = AsyncBoltRequest(
            body="",
            query=f"code=foo&state={state}",
            headers={"cookie": [f"{oauth_flow.settings.state_cookie_name}={state}"]},
        )
        resp = await oauth_flow.handle_callback(req)
        assert resp.status == 200
        assert resp.body == "customized"

        req = AsyncBoltRequest(
            body="",
            query=f"code=foo&state=invalid",
            headers={"cookie": [f"{oauth_flow.settings.state_cookie_name}={state}"]},
        )
        resp = await oauth_flow.handle_callback(req)
        assert resp.status == 502
        assert resp.body == "customized"
