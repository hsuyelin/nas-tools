import asyncio
import datetime
import json
import logging
from time import time
from typing import Optional

import pytest
from slack_sdk.errors import SlackApiError
from slack_sdk.oauth.installation_store import Installation, Bot
from slack_sdk.oauth.installation_store.async_installation_store import (
    AsyncInstallationStore,
)
from slack_sdk.signature import SignatureVerifier
from slack_sdk.web.async_client import AsyncWebClient

from slack_bolt.app.async_app import AsyncApp
from slack_bolt.authorization import AuthorizeResult
from slack_bolt.authorization.async_authorize import AsyncAuthorize
from slack_bolt.context.async_context import AsyncBoltContext
from slack_bolt.error import BoltError
from slack_bolt.oauth.async_oauth_settings import AsyncOAuthSettings
from slack_bolt.request.async_request import AsyncBoltRequest
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
    assert_auth_test_count_async,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestAppCustomAuthorize:
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

    def build_valid_app_mention_request(self) -> AsyncBoltRequest:
        timestamp, body = str(int(time())), json.dumps(app_mention_body)
        return AsyncBoltRequest(body=body, headers=self.build_headers(timestamp, body))

    @pytest.mark.asyncio
    async def test_installation_store_only(self):
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
            oauth_settings=AsyncOAuthSettings(
                client_id="111.222",
                client_secret="secret",
                installation_store=MemoryInstallationStore(),
            ),
        )
        app.event("app_mention")(whats_up)

        request = self.build_valid_app_mention_request()
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)
        await asyncio.sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    @pytest.mark.asyncio
    async def test_installation_store_and_authorize(self):
        installation_store = MemoryInstallationStore()
        app = AsyncApp(
            client=self.web_client,
            signing_secret=self.signing_secret,
            authorize=CustomAuthorize(installation_store),
            oauth_settings=AsyncOAuthSettings(
                client_id="111.222",
                client_secret="secret",
                installation_store=installation_store,
            ),
        )
        app.event("app_mention")(whats_up)

        request = self.build_valid_app_mention_request()
        response = await app.async_dispatch(request)
        assert response.status == 200
        await assert_auth_test_count_async(self, 1)
        await asyncio.sleep(1)  # wait a bit after auto ack()
        assert self.mock_received_requests["/chat.postMessage"] == 1

    @pytest.mark.asyncio
    async def test_installation_store_and_func_authorize(self):
        installation_store = MemoryInstallationStore()

        async def authorize():
            pass

        with pytest.raises(BoltError):
            AsyncApp(
                client=self.web_client,
                signing_secret=self.signing_secret,
                authorize=authorize,
                oauth_settings=AsyncOAuthSettings(
                    client_id="111.222",
                    client_secret="secret",
                    installation_store=installation_store,
                ),
            )


app_mention_body = {
    "token": "verification_token",
    "team_id": "T111",
    "enterprise_id": "E111",
    "api_app_id": "A111",
    "event": {
        "client_msg_id": "9cbd4c5b-7ddf-4ede-b479-ad21fca66d63",
        "type": "app_mention",
        "text": "<@W111> Hi there!",
        "user": "W222",
        "ts": "1595926230.009600",
        "team": "T111",
        "channel": "C111",
        "event_ts": "1595926230.009600",
    },
    "type": "event_callback",
    "event_id": "Ev111",
    "event_time": 1595926230,
    "authed_users": ["W111"],
}


async def whats_up(body, say, payload, event):
    assert body["event"] == payload
    assert payload == event
    await say("What's up?")


class MemoryInstallationStore(AsyncInstallationStore):
    @property
    def logger(self) -> logging.Logger:
        return logging.getLogger(__name__)

    async def async_save(self, installation: Installation):
        pass

    async def async_find_bot(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Bot]:
        return Bot(
            app_id="A111",
            enterprise_id="E111",
            team_id="T0G9PQBBK",
            bot_token="xoxb-valid",
            bot_id="B",
            bot_user_id="W",
            bot_scopes=["commands", "chat:write"],
            installed_at=datetime.datetime.now().timestamp(),
        )

    async def async_find_installation(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        user_id: Optional[str] = None,
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Installation]:
        return Installation(
            app_id="A111",
            enterprise_id="E111",
            team_id="T0G9PQBBK",
            bot_token="xoxb-valid-2",
            bot_id="B",
            bot_user_id="W",
            bot_scopes=["commands", "chat:write"],
            user_id="W11111",
            user_token="xoxp-valid",
            user_scopes=["search:read"],
            installed_at=datetime.datetime.now().timestamp(),
        )


class CustomAuthorize(AsyncAuthorize):
    def __init__(self, installation_store: AsyncInstallationStore):
        self.installation_store = installation_store

    async def __call__(
        self,
        *,
        context: AsyncBoltContext,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        user_id: Optional[str],
    ) -> Optional[AuthorizeResult]:
        bot_token: Optional[str] = None
        user_token: Optional[str] = None
        latest_installation: Optional[Installation] = await self.installation_store.async_find_installation(
            enterprise_id=enterprise_id,
            team_id=team_id,
            is_enterprise_install=context.is_enterprise_install,
        )
        this_user_installation: Optional[Installation] = None
        if latest_installation is not None:
            bot_token = latest_installation.bot_token  # this still can be None
            user_token = latest_installation.user_token  # this still can be None
            if latest_installation.user_id != user_id:
                # First off, remove the user token as the installer is a different user
                user_token = None
                latest_installation.user_token = None
                latest_installation.user_refresh_token = None
                latest_installation.user_token_expires_at = None
                latest_installation.user_scopes = []

                # try to fetch the request user's installation
                # to reflect the user's access token if exists
                this_user_installation = await self.installation_store.async_find_installation(
                    enterprise_id=enterprise_id,
                    team_id=team_id,
                    user_id=user_id,
                    is_enterprise_install=context.is_enterprise_install,
                )
                if this_user_installation is not None:
                    user_token = this_user_installation.user_token
                    if latest_installation.bot_token is None:
                        # If latest_installation has a bot token, we never overwrite the value
                        bot_token = this_user_installation.bot_token
        token: Optional[str] = bot_token or user_token
        if token is None:
            return None
        try:
            auth_test_api_response = await context.client.auth_test(token=token)
            authorize_result = AuthorizeResult.from_auth_test_response(
                auth_test_response=auth_test_api_response,
                bot_token=bot_token,
                user_token=user_token,
            )
            return authorize_result
        except SlackApiError:
            return None
