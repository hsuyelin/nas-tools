import asyncio
import json
from time import time
from urllib.parse import quote

import pytest
from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.oauth.state_store import FileOAuthStateStore
from slack_sdk.oauth.state_store.async_state_store import AsyncOAuthStateStore
from slack_sdk.signature import SignatureVerifier
from slack_sdk.web.async_client import AsyncWebClient

from slack_bolt import BoltResponse
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.error import BoltError
from slack_bolt.oauth.async_callback_options import (
    AsyncFailureArgs,
    AsyncSuccessArgs,
    AsyncCallbackOptions,
)
from slack_bolt.oauth.async_oauth_flow import AsyncOAuthFlow
from slack_bolt.oauth.async_oauth_settings import AsyncOAuthSettings
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_bolt.request.async_request import AsyncBoltRequest
from tests.mock_web_api_server import (
    cleanup_mock_web_api_server,
    setup_mock_web_api_server,
    assert_auth_test_count_async,
)


class TestAsyncOAuthFlow:
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
        oauth_flow = AsyncOAuthFlow(
            settings=AsyncOAuthSettings(
                client_id="111.222",
                client_secret="xxx",
                scopes=["chat:write", "commands"],
                user_scopes=["search:read"],
                installation_store=FileInstallationStore(),
                state_store=FileOAuthStateStore(expiration_seconds=120),
            )
        )
        assert oauth_flow is not None
        assert oauth_flow.logger is not None
        assert oauth_flow.client is not None

    @pytest.mark.asyncio
    async def test_scopes_as_str(self):
        settings = AsyncOAuthSettings(
            client_id="111.222",
            client_secret="xxx",
            scopes="chat:write,commands",
            user_scopes="search:read",
        )
        assert settings.scopes == ["chat:write", "commands"]
        assert settings.user_scopes == ["search:read"]

    @pytest.mark.asyncio
    async def test_instantiation_non_async_settings(self):
        with pytest.raises(BoltError):
            AsyncOAuthFlow(
                settings=OAuthSettings(
                    client_id="111.222",
                    client_secret="xxx",
                    scopes="chat:write,commands",
                )
            )

    @pytest.mark.asyncio
    async def test_instantiation_non_async_settings_to_app(self):
        with pytest.raises(BoltError):
            AsyncApp(
                signing_secret="xxx",
                oauth_settings=OAuthSettings(
                    client_id="111.222",
                    client_secret="xxx",
                    scopes="chat:write,commands",
                ),
            )

    @pytest.mark.asyncio
    async def test_handle_installation_default(self):
        oauth_flow = AsyncOAuthFlow(
            settings=AsyncOAuthSettings(
                client_id="111.222",
                client_secret="xxx",
                scopes=["chat:write", "commands"],
                installation_store=FileInstallationStore(),
                state_store=FileOAuthStateStore(expiration_seconds=120),
            )
        )
        req = AsyncBoltRequest(body="")
        resp = await oauth_flow.handle_installation(req)
        assert resp.status == 200
        assert resp.headers.get("content-type") == ["text/html; charset=utf-8"]
        assert "https://slack.com/oauth/v2/authorize?state=" in resp.body
        assert resp.headers.get("set-cookie") is not None

    @pytest.mark.asyncio
    async def test_handle_installation_no_rendering(self):
        oauth_flow = AsyncOAuthFlow(
            settings=AsyncOAuthSettings(
                client_id="111.222",
                client_secret="xxx",
                scopes=["chat:write", "commands"],
                installation_store=FileInstallationStore(),
                install_page_rendering_enabled=False,  # disabled
                state_store=FileOAuthStateStore(expiration_seconds=120),
            )
        )
        req = AsyncBoltRequest(body="")
        resp = await oauth_flow.handle_installation(req)
        assert resp.status == 302
        location_header = resp.headers.get("location")[0]
        assert "https://slack.com/oauth/v2/authorize?state=" in location_header
        assert resp.headers.get("set-cookie") is not None

    @pytest.mark.asyncio
    async def test_handle_installation_team_param(self):
        oauth_flow = AsyncOAuthFlow(
            settings=AsyncOAuthSettings(
                client_id="111.222",
                client_secret="xxx",
                scopes=["chat:write", "commands"],
                installation_store=FileInstallationStore(),
                install_page_rendering_enabled=False,  # disabled
                state_store=FileOAuthStateStore(expiration_seconds=120),
            )
        )
        req = AsyncBoltRequest(body="", query={"team": "T12345"})
        resp = await oauth_flow.handle_installation(req)
        assert resp.status == 302
        location_header = resp.headers.get("location")[0]
        assert "https://slack.com/oauth/v2/authorize?state=" in location_header
        assert "&team=T12345" in location_header
        assert resp.headers.get("set-cookie") is not None

    @pytest.mark.asyncio
    async def test_handle_installation_no_state_validation(self):
        oauth_flow = AsyncOAuthFlow(
            settings=AsyncOAuthSettings(
                client_id="111.222",
                client_secret="xxx",
                scopes=["chat:write", "commands"],
                installation_store=FileInstallationStore(),
                install_page_rendering_enabled=False,  # disabled
                state_validation_enabled=False,  # disabled
                state_store=FileOAuthStateStore(expiration_seconds=120),
            )
        )
        req = AsyncBoltRequest(body="")
        resp = await oauth_flow.handle_installation(req)
        assert resp.status == 302
        location_header = resp.headers.get("location")[0]
        assert "https://slack.com/oauth/v2/authorize?state=" in location_header
        assert resp.headers.get("set-cookie") is None

    @pytest.mark.asyncio
    async def test_handle_callback(self):
        oauth_flow = AsyncOAuthFlow(
            client=AsyncWebClient(base_url=self.mock_api_server_base_url),
            settings=AsyncOAuthSettings(
                client_id="111.222",
                client_secret="xxx",
                scopes=["chat:write", "commands"],
                installation_store=FileInstallationStore(),
                state_store=FileOAuthStateStore(expiration_seconds=120),
                success_url="https://www.example.com/completion",
                failure_url="https://www.example.com/failure",
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
        assert "https://www.example.com/completion" in resp.body

        app = AsyncApp(signing_secret="signing_secret", oauth_flow=oauth_flow)
        global_shortcut_body = {
            "type": "shortcut",
            "token": "verification_token",
            "action_ts": "111.111",
            "team": {
                "id": "T111",
                "domain": "workspace-domain",
                "enterprise_id": "E111",
                "enterprise_name": "Org Name",
            },
            "user": {"id": "W111", "username": "primary-owner", "team_id": "T111"},
            "callback_id": "test-shortcut",
            "trigger_id": "111.111.xxxxxx",
        }
        body = f"payload={quote(json.dumps(global_shortcut_body))}"
        timestamp = str(int(time()))
        signature_verifier = SignatureVerifier("signing_secret")
        headers = {
            "content-type": ["application/x-www-form-urlencoded"],
            "x-slack-signature": [signature_verifier.generate_signature(body=body, timestamp=timestamp)],
            "x-slack-request-timestamp": [timestamp],
        }
        request = AsyncBoltRequest(body=body, headers=headers)
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)

    @pytest.mark.asyncio
    async def test_handle_callback_invalid_state(self):
        oauth_flow = AsyncOAuthFlow(
            settings=AsyncOAuthSettings(
                client_id="111.222",
                client_secret="xxx",
                scopes=["chat:write", "commands"],
                installation_store=FileInstallationStore(),
                state_store=FileOAuthStateStore(expiration_seconds=120),
            )
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
    async def test_handle_callback_invalid_state(self):
        class MyOAuthStateStore(AsyncOAuthStateStore):
            async def async_issue(self, *args, **kwargs) -> str:
                return "expired_one"

            async def async_consume(self, state: str) -> bool:
                return False

        oauth_flow = AsyncOAuthFlow(
            settings=AsyncOAuthSettings(
                client_id="111.222",
                client_secret="xxx",
                scopes=["chat:write", "commands"],
                state_store=MyOAuthStateStore(),
            )
        )
        state = await oauth_flow.issue_new_state(None)
        req = AsyncBoltRequest(
            body="",
            query=f"code=foo&state={state}",
            headers={"cookie": [f"{oauth_flow.settings.state_cookie_name}={state}"]},
        )
        resp = await oauth_flow.handle_callback(req)
        assert resp.status == 401

    @pytest.mark.asyncio
    async def test_handle_callback_no_state_validation(self):
        oauth_flow = AsyncOAuthFlow(
            client=AsyncWebClient(base_url=self.mock_api_server_base_url),
            settings=AsyncOAuthSettings(
                client_id="111.222",
                client_secret="xxx",
                scopes=["chat:write", "commands"],
                installation_store=FileInstallationStore(),
                state_validation_enabled=False,  # disabled
                state_store=None,
            ),
        )
        state = await oauth_flow.issue_new_state(None)
        req = AsyncBoltRequest(
            body="",
            query=f"code=foo&state=invalid",
            headers={"cookie": [f"{oauth_flow.settings.state_cookie_name}={state}"]},
        )
        resp = await oauth_flow.handle_callback(req)
        assert resp.status == 200

    @pytest.mark.asyncio
    async def test_handle_callback_using_options(self):
        async def success(args: AsyncSuccessArgs) -> BoltResponse:
            assert args.request is not None
            return BoltResponse(status=200, body="customized")

        async def failure(args: AsyncFailureArgs) -> BoltResponse:
            assert args.request is not None
            assert args.reason is not None
            return BoltResponse(status=502, body="customized")

        oauth_flow = AsyncOAuthFlow(
            client=AsyncWebClient(base_url=self.mock_api_server_base_url),
            settings=AsyncOAuthSettings(
                client_id="111.222",
                client_secret="xxx",
                scopes=["chat:write", "commands"],
                installation_store=FileInstallationStore(),
                state_store=FileOAuthStateStore(expiration_seconds=120),
                callback_options=AsyncCallbackOptions(
                    success=success,
                    failure=failure,
                ),
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
