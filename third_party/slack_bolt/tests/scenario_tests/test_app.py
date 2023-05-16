import logging
import time
from concurrent.futures import Executor
from ssl import SSLContext

import pytest
from slack_sdk import WebClient
from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.oauth.state_store import FileOAuthStateStore

from slack_bolt import App, Say, BoltRequest, BoltContext
from slack_bolt.authorization import AuthorizeResult
from slack_bolt.error import BoltError
from slack_bolt.oauth import OAuthFlow
from slack_bolt.oauth.oauth_settings import OAuthSettings
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestApp:
    signing_secret = "secret"
    valid_token = "xoxb-valid"
    mock_api_server_base_url = "http://localhost:8888"
    web_client = WebClient(
        token=valid_token,
        base_url=mock_api_server_base_url,
    )

    def setup_method(self):
        self.old_os_env = remove_os_env_temporarily()
        setup_mock_web_api_server(self)

    def teardown_method(self):
        cleanup_mock_web_api_server(self)
        restore_os_env(self.old_os_env)

    @staticmethod
    def handle_app_mention(body, say: Say, payload, event):
        assert body["event"] == payload
        assert payload == event
        say("What's up?")

    # --------------------------
    # basic tests
    # --------------------------

    def simple_listener(self, ack):
        ack()

    def test_listener_registration_error(self):
        app = App(signing_secret="valid", client=self.web_client)
        with pytest.raises(BoltError):
            app.action({"type": "invalid_type", "action_id": "a"})(self.simple_listener)

    def test_listener_executor(self):
        class TestExecutor(Executor):
            """A executor that does nothing for testing"""

            pass

        executor = TestExecutor()
        app = App(
            signing_secret="valid",
            client=self.web_client,
            listener_executor=executor,
        )

        assert app.listener_runner.listener_executor == executor
        assert app.listener_runner.lazy_listener_runner.executor == executor

    # --------------------------
    # single team auth
    # --------------------------

    def test_valid_single_auth(self):
        app = App(signing_secret="valid", client=self.web_client)
        assert app != None

    def test_token_absence(self):
        with pytest.raises(BoltError):
            App(signing_secret="valid", token=None)
        with pytest.raises(BoltError):
            App(signing_secret="valid", token="")

    def test_token_verification_enabled_False(self):
        App(
            signing_secret="valid",
            client=self.web_client,
            token_verification_enabled=False,
        )
        App(
            signing_secret="valid",
            token="xoxb-invalid",
            token_verification_enabled=False,
        )

        assert self.mock_received_requests.get("/auth.test") is None

    # --------------------------
    # multi teams auth
    # --------------------------

    def test_valid_multi_auth(self):
        app = App(
            signing_secret="valid",
            oauth_settings=OAuthSettings(client_id="111.222", client_secret="valid"),
        )
        assert app != None

    def test_valid_multi_auth_oauth_flow(self):
        oauth_flow = OAuthFlow(
            settings=OAuthSettings(
                client_id="111.222",
                client_secret="valid",
                installation_store=FileInstallationStore(),
                state_store=FileOAuthStateStore(expiration_seconds=120),
            )
        )
        app = App(signing_secret="valid", oauth_flow=oauth_flow)
        assert app != None

    def test_valid_multi_auth_client_id_absence(self):
        with pytest.raises(BoltError):
            App(
                signing_secret="valid",
                oauth_settings=OAuthSettings(client_id=None, client_secret="valid"),
            )

    def test_valid_multi_auth_secret_absence(self):
        with pytest.raises(BoltError):
            App(
                signing_secret="valid",
                oauth_settings=OAuthSettings(client_id="111.222", client_secret=None),
            )

    def test_authorize_conflicts(self):
        oauth_settings = OAuthSettings(
            client_id="111.222",
            client_secret="valid",
            installation_store=FileInstallationStore(),
            state_store=FileOAuthStateStore(expiration_seconds=120),
        )

        # no error with this
        App(signing_secret="valid", oauth_settings=oauth_settings)

        def authorize() -> AuthorizeResult:
            return AuthorizeResult(enterprise_id="E111", team_id="T111")

        with pytest.raises(BoltError):
            App(
                signing_secret="valid",
                authorize=authorize,
                oauth_settings=oauth_settings,
            )

        oauth_flow = OAuthFlow(settings=oauth_settings)
        # no error with this
        App(signing_secret="valid", oauth_flow=oauth_flow)

        with pytest.raises(BoltError):
            App(signing_secret="valid", authorize=authorize, oauth_flow=oauth_flow)

    def test_installation_store_conflicts(self):
        store1 = FileInstallationStore()
        store2 = FileInstallationStore()
        app = App(
            signing_secret="valid",
            oauth_settings=OAuthSettings(
                client_id="111.222",
                client_secret="valid",
                installation_store=store1,
            ),
            installation_store=store2,
        )
        assert app.installation_store is store1

        app = App(
            signing_secret="valid",
            oauth_flow=OAuthFlow(
                settings=OAuthSettings(
                    client_id="111.222",
                    client_secret="valid",
                    installation_store=store1,
                )
            ),
            installation_store=store2,
        )
        assert app.installation_store is store1

        app = App(
            signing_secret="valid",
            oauth_flow=OAuthFlow(
                settings=OAuthSettings(
                    client_id="111.222",
                    client_secret="valid",
                )
            ),
            installation_store=store1,
        )
        assert app.installation_store is store1

    def test_none_body(self):
        app = App(signing_secret="valid", client=self.web_client)

        req = BoltRequest(body=None, headers={}, mode="http")
        response = app.dispatch(req)
        # request verification failure
        assert response.status == 401
        assert response.body == '{"error": "invalid request"}'

        req = BoltRequest(body=None, headers={}, mode="socket_mode")
        response = app.dispatch(req)
        # request verification is skipped for Socket Mode
        assert response.status == 404
        assert response.body == '{"error": "unhandled request"}'

    def test_none_body_no_middleware(self):
        app = App(
            signing_secret="valid",
            client=self.web_client,
            ssl_check_enabled=False,
            ignoring_self_events_enabled=False,
            request_verification_enabled=False,
            token_verification_enabled=False,
            url_verification_enabled=False,
        )
        req = BoltRequest(body=None, headers={}, mode="http")
        response = app.dispatch(req)
        assert response.status == 404
        assert response.body == '{"error": "unhandled request"}'

        req = BoltRequest(body=None, headers={}, mode="socket_mode")
        response = app.dispatch(req)
        assert response.status == 404
        assert response.body == '{"error": "unhandled request"}'

    def test_proxy_ssl_for_respond(self):
        ssl = SSLContext()
        web_client = WebClient(
            token=self.valid_token,
            base_url=self.mock_api_server_base_url,
            proxy="http://proxy-host:9000/",
            ssl=ssl,
        )
        app = App(
            signing_secret="valid",
            client=web_client,
            authorize=lambda: AuthorizeResult(
                enterprise_id="E111",
                team_id="T111",
            ),
        )

        result = {"called": False}

        @app.event("app_mention")
        def handle(context: BoltContext, respond):
            assert context.respond.proxy == "http://proxy-host:9000/"
            assert context.respond.ssl == ssl
            assert respond.proxy == "http://proxy-host:9000/"
            assert respond.ssl == ssl
            result["called"] = True

        req = BoltRequest(body=app_mention_event_body, headers={}, mode="socket_mode")
        response = app.dispatch(req)
        assert response.status == 200
        assert result["called"] is True

    def test_argument_logger_propagation(self):
        custom_logger = logging.getLogger(f"{__name__}-{time.time()}-logger-test")
        custom_logger.setLevel(logging.INFO)
        added_handler = logging.NullHandler()
        custom_logger.addHandler(added_handler)
        added_filter = logging.Filter()
        custom_logger.addFilter(added_filter)

        app = App(
            signing_secret="valid",
            client=WebClient(
                token=self.valid_token,
                base_url=self.mock_api_server_base_url,
            ),
            authorize=lambda: AuthorizeResult(
                enterprise_id="E111",
                team_id="T111",
            ),
            logger=custom_logger,
        )
        result = {"called": False}

        def _verify_logger(logger: logging.Logger):
            assert logger.level == custom_logger.level
            assert len(logger.handlers) == len(custom_logger.handlers)
            assert logger.handlers[-1] == custom_logger.handlers[-1]
            assert len(logger.filters) == len(custom_logger.filters)
            assert logger.filters[-1] == custom_logger.filters[-1]

        @app.use
        def global_middleware(logger, next):
            _verify_logger(logger)
            next()

        def listener_middleware(logger, next):
            _verify_logger(logger)
            next()

        def listener_matcher(logger):
            _verify_logger(logger)
            return True

        @app.event(
            "app_mention",
            middleware=[listener_middleware],
            matchers=[listener_matcher],
        )
        def handle(logger: logging.Logger):
            _verify_logger(logger)
            result["called"] = True

        req = BoltRequest(body=app_mention_event_body, headers={}, mode="socket_mode")
        response = app.dispatch(req)
        assert response.status == 200
        assert result["called"] is True


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
