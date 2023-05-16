import asyncio
import logging
from ssl import SSLContext

import pytest
from slack_sdk import WebClient
from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.oauth.state_store import FileOAuthStateStore
from slack_sdk.web.async_client import AsyncWebClient

from slack_bolt.async_app import AsyncApp
from slack_bolt.authorization import AuthorizeResult
from slack_bolt.context.async_context import AsyncBoltContext
from slack_bolt.error import BoltError
from slack_bolt.oauth.async_oauth_flow import AsyncOAuthFlow
from slack_bolt.oauth.async_oauth_settings import AsyncOAuthSettings
from slack_bolt.request.async_request import AsyncBoltRequest
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestAsyncApp:
    signing_secret = "secret"
    valid_token = "xoxb-valid"
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

    def setup_method(self):
        self.old_os_env = remove_os_env_temporarily()

    def teardown_method(self):
        restore_os_env(self.old_os_env)

    def non_coro_func(self, ack):
        ack()

    def test_non_coroutine_func_listener(self):
        app = AsyncApp(signing_secret="valid", token="xoxb-xxx")
        with pytest.raises(BoltError):
            app.action("a")(self.non_coro_func)

    async def simple_listener(self, ack):
        await ack()

    def test_listener_registration_error(self):
        app = AsyncApp(signing_secret="valid", token="xoxb-xxx")
        with pytest.raises(BoltError):
            app.action({"type": "invalid_type", "action_id": "a"})(self.simple_listener)

    # NOTE: We intentionally don't have this test in scenario_tests
    # to avoid having async dependencies in the tests.
    def test_invalid_client_type(self):
        with pytest.raises(BoltError):
            AsyncApp(signing_secret="valid", client=WebClient(token="xoxb-xxx"))

    # --------------------------
    # single team auth
    # --------------------------

    def test_valid_single_auth(self):
        app = AsyncApp(signing_secret="valid", token="xoxb-xxx")
        assert app != None

    def test_token_absence(self):
        with pytest.raises(BoltError):
            AsyncApp(signing_secret="valid", token=None)
        with pytest.raises(BoltError):
            AsyncApp(signing_secret="valid", token="")

    # --------------------------
    # multi teams auth
    # --------------------------

    def test_valid_multi_auth(self):
        app = AsyncApp(
            signing_secret="valid",
            oauth_settings=AsyncOAuthSettings(client_id="111.222", client_secret="valid"),
        )
        assert app != None

    def test_valid_multi_auth_oauth_flow(self):
        oauth_flow = AsyncOAuthFlow(
            settings=AsyncOAuthSettings(
                client_id="111.222",
                client_secret="valid",
                installation_store=FileInstallationStore(),
                state_store=FileOAuthStateStore(expiration_seconds=120),
            )
        )
        app = AsyncApp(signing_secret="valid", oauth_flow=oauth_flow)
        assert app != None

    def test_valid_multi_auth_client_id_absence(self):
        with pytest.raises(BoltError):
            AsyncApp(
                signing_secret="valid",
                oauth_settings=AsyncOAuthSettings(client_id=None, client_secret="valid"),
            )

    def test_valid_multi_auth_secret_absence(self):
        with pytest.raises(BoltError):
            AsyncApp(
                signing_secret="valid",
                oauth_settings=AsyncOAuthSettings(client_id="111.222", client_secret=None),
            )

    def test_authorize_conflicts(self):
        oauth_settings = AsyncOAuthSettings(
            client_id="111.222",
            client_secret="valid",
            installation_store=FileInstallationStore(),
            state_store=FileOAuthStateStore(expiration_seconds=120),
        )

        # no error with this
        AsyncApp(signing_secret="valid", oauth_settings=oauth_settings)

        def authorize() -> AuthorizeResult:
            return AuthorizeResult(enterprise_id="E111", team_id="T111")

        with pytest.raises(BoltError):
            AsyncApp(
                signing_secret="valid",
                authorize=authorize,
                oauth_settings=oauth_settings,
            )

        oauth_flow = AsyncOAuthFlow(settings=oauth_settings)
        # no error with this
        AsyncApp(signing_secret="valid", oauth_flow=oauth_flow)

        with pytest.raises(BoltError):
            AsyncApp(signing_secret="valid", authorize=authorize, oauth_flow=oauth_flow)

    def test_installation_store_conflicts(self):
        store1 = FileInstallationStore()
        store2 = FileInstallationStore()
        app = AsyncApp(
            signing_secret="valid",
            oauth_settings=AsyncOAuthSettings(
                client_id="111.222",
                client_secret="valid",
                installation_store=store1,
            ),
            installation_store=store2,
        )
        assert app.installation_store is store1

        app = AsyncApp(
            signing_secret="valid",
            oauth_flow=AsyncOAuthFlow(
                settings=AsyncOAuthSettings(
                    client_id="111.222",
                    client_secret="valid",
                    installation_store=store1,
                )
            ),
            installation_store=store2,
        )
        assert app.installation_store is store1

        app = AsyncApp(
            signing_secret="valid",
            oauth_flow=AsyncOAuthFlow(
                settings=AsyncOAuthSettings(
                    client_id="111.222",
                    client_secret="valid",
                )
            ),
            installation_store=store1,
        )
        assert app.installation_store is store1

    @pytest.mark.asyncio
    async def test_proxy_ssl_for_respond(self):
        ssl = SSLContext()
        app = AsyncApp(
            signing_secret="valid",
            client=AsyncWebClient(
                token=self.valid_token,
                base_url=self.mock_api_server_base_url,
                proxy="http://proxy-host:9000/",
                ssl=ssl,
            ),
            authorize=my_authorize,
        )

        result = {"called": False}

        @app.event("app_mention")
        async def handle(context: AsyncBoltContext, respond):
            assert context.respond.proxy == "http://proxy-host:9000/"
            assert context.respond.ssl == ssl
            assert respond.proxy == "http://proxy-host:9000/"
            assert respond.ssl == ssl
            result["called"] = True

        req = AsyncBoltRequest(body=app_mention_event_body, headers={}, mode="socket_mode")
        response = await app.async_dispatch(req)
        assert response.status == 200
        await asyncio.sleep(0.5)  # wait a bit after auto ack()
        assert result["called"] is True

    @pytest.mark.asyncio
    async def test_argument_logger_propagation(self):
        import time

        custom_logger = logging.getLogger(f"{__name__}-{time.time()}-async-logger-test")
        custom_logger.setLevel(logging.INFO)
        added_handler = logging.NullHandler()
        custom_logger.addHandler(added_handler)
        added_filter = logging.Filter()
        custom_logger.addFilter(added_filter)

        app = AsyncApp(
            signing_secret="valid",
            client=AsyncWebClient(
                token=self.valid_token,
                base_url=self.mock_api_server_base_url,
            ),
            authorize=my_authorize,
            logger=custom_logger,
        )

        result = {"called": False}

        def _verify_logger(logger: logging.Logger):
            assert logger.level == custom_logger.level
            assert len(logger.handlers) == len(custom_logger.handlers)
            # TODO: this assertion fails only with codecov
            # assert logger.handlers[-1] == custom_logger.handlers[-1]
            assert logger.handlers[-1].name == custom_logger.handlers[-1].name
            assert len(logger.filters) == len(custom_logger.filters)
            # TODO: this assertion fails only with codecov
            # assert logger.filters[-1] == custom_logger.filters[-1]
            assert logger.filters[-1].name == custom_logger.filters[-1].name

        @app.use
        async def global_middleware(logger, next):
            _verify_logger(logger)
            await next()

        async def listener_middleware(logger, next):
            _verify_logger(logger)
            await next()

        async def listener_matcher(logger):
            _verify_logger(logger)
            return True

        @app.event(
            "app_mention",
            middleware=[listener_middleware],
            matchers=[listener_matcher],
        )
        async def handle(logger: logging.Logger):
            _verify_logger(logger)
            result["called"] = True

        req = AsyncBoltRequest(body=app_mention_event_body, headers={}, mode="socket_mode")
        response = await app.async_dispatch(req)
        assert response.status == 200
        await asyncio.sleep(0.5)  # wait a bit after auto ack()
        assert result["called"] is True


async def my_authorize():
    return AuthorizeResult(
        enterprise_id="E111",
        team_id="T111",
    )


app_mention_event_body = {
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
}
