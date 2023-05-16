import json
from time import time
from urllib.parse import quote

from slack_sdk import WebClient
from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.oauth.state_store import (
    OAuthStateStore,
    FileOAuthStateStore,
)
from slack_sdk.signature import SignatureVerifier

from slack_bolt import BoltRequest, BoltResponse, App
from slack_bolt.oauth import OAuthFlow
from slack_bolt.oauth.callback_options import CallbackOptions, SuccessArgs, FailureArgs
from slack_bolt.oauth.oauth_settings import OAuthSettings
from tests.mock_web_api_server import (
    cleanup_mock_web_api_server,
    setup_mock_web_api_server,
    assert_auth_test_count,
)


class TestOAuthFlow:
    mock_api_server_base_url = "http://localhost:8888"

    def setup_method(self):
        setup_mock_web_api_server(self)

    def teardown_method(self):
        cleanup_mock_web_api_server(self)

    def test_instantiation(self):
        oauth_flow = OAuthFlow(
            settings=OAuthSettings(
                client_id="111.222",
                client_secret="xxx",
                scopes=["chat:write", "commands"],
                installation_store=FileInstallationStore(),
                state_store=FileOAuthStateStore(expiration_seconds=120),
            )
        )
        assert oauth_flow is not None
        assert oauth_flow.logger is not None
        assert oauth_flow.client is not None

    def test_handle_installation_default(self):
        oauth_flow = OAuthFlow(
            settings=OAuthSettings(
                client_id="111.222",
                client_secret="xxx",
                scopes=["chat:write", "commands"],
                user_scopes=["search:read"],
                installation_store=FileInstallationStore(),
                state_store=FileOAuthStateStore(expiration_seconds=120),
            )
        )
        req = BoltRequest(body="")
        resp = oauth_flow.handle_installation(req)
        assert resp.status == 200
        assert resp.headers.get("content-type") == ["text/html; charset=utf-8"]
        assert resp.headers.get("set-cookie") is not None
        assert "https://slack.com/oauth/v2/authorize?state=" in resp.body

    # https://github.com/slackapi/bolt-python/issues/183
    # For direct install URL support
    def test_handle_installation_no_rendering(self):
        oauth_flow = OAuthFlow(
            settings=OAuthSettings(
                client_id="111.222",
                client_secret="xxx",
                scopes=["chat:write", "commands"],
                user_scopes=["search:read"],
                installation_store=FileInstallationStore(),
                install_page_rendering_enabled=False,  # disabled
                state_store=FileOAuthStateStore(expiration_seconds=120),
            )
        )
        req = BoltRequest(body="")
        resp = oauth_flow.handle_installation(req)
        assert resp.status == 302
        location_header = resp.headers.get("location")[0]
        assert "https://slack.com/oauth/v2/authorize?state=" in location_header
        assert resp.headers.get("set-cookie") is not None

    def test_handle_installation_team_param(self):
        oauth_flow = OAuthFlow(
            settings=OAuthSettings(
                client_id="111.222",
                client_secret="xxx",
                scopes=["chat:write", "commands"],
                user_scopes=["search:read"],
                installation_store=FileInstallationStore(),
                install_page_rendering_enabled=False,  # disabled
                state_store=FileOAuthStateStore(expiration_seconds=120),
            )
        )
        req = BoltRequest(body="", query={"team": "T12345"})
        resp = oauth_flow.handle_installation(req)
        assert resp.status == 302
        location_header = resp.headers.get("location")[0]
        assert "https://slack.com/oauth/v2/authorize?state=" in location_header
        assert "&team=T12345" in location_header
        assert resp.headers.get("set-cookie") is not None

    def test_handle_installation_no_state_validation(self):
        oauth_flow = OAuthFlow(
            settings=OAuthSettings(
                client_id="111.222",
                client_secret="xxx",
                scopes=["chat:write", "commands"],
                user_scopes=["search:read"],
                installation_store=FileInstallationStore(),
                install_page_rendering_enabled=False,  # disabled
                state_validation_enabled=False,  # disabled
                state_store=None,
            )
        )
        req = BoltRequest(body="")
        resp = oauth_flow.handle_installation(req)
        assert resp.status == 302
        assert resp.headers.get("set-cookie") is None

    def test_scopes_as_str(self):
        settings = OAuthSettings(
            client_id="111.222",
            client_secret="xxx",
            scopes="chat:write,commands",
            user_scopes="search:read",
        )
        assert settings.scopes == ["chat:write", "commands"]
        assert settings.user_scopes == ["search:read"]

    def test_handle_callback(self):
        oauth_flow = OAuthFlow(
            client=WebClient(base_url=self.mock_api_server_base_url),
            settings=OAuthSettings(
                client_id="111.222",
                client_secret="xxx",
                scopes=["chat:write", "commands"],
                installation_store=FileInstallationStore(),
                state_store=FileOAuthStateStore(expiration_seconds=120),
                success_url="https://www.example.com/completion",
                failure_url="https://www.example.com/failure",
            ),
        )
        state = oauth_flow.issue_new_state(None)
        req = BoltRequest(
            body="",
            query=f"code=foo&state={state}",
            headers={"cookie": [f"{oauth_flow.settings.state_cookie_name}={state}"]},
        )
        resp = oauth_flow.handle_callback(req)
        assert resp.status == 200
        assert "https://www.example.com/completion" in resp.body

        app = App(signing_secret="signing_secret", oauth_flow=oauth_flow)
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
        request = BoltRequest(body=body, headers=headers)
        response = app.dispatch(request)
        assert response.status == 200
        assert_auth_test_count(self, 1)

    def test_handle_callback_invalid_state(self):
        oauth_flow = OAuthFlow(
            settings=OAuthSettings(
                client_id="111.222",
                client_secret="xxx",
                scopes=["chat:write", "commands"],
                installation_store=FileInstallationStore(),
                state_store=FileOAuthStateStore(expiration_seconds=120),
            )
        )
        state = oauth_flow.issue_new_state(None)
        req = BoltRequest(
            body="",
            query=f"code=foo&state=invalid",
            headers={"cookie": [f"{oauth_flow.settings.state_cookie_name}={state}"]},
        )
        resp = oauth_flow.handle_callback(req)
        assert resp.status == 400

    def test_handle_callback_already_expired_state(self):
        class MyOAuthStateStore(OAuthStateStore):
            def issue(self, *args, **kwargs) -> str:
                return "expired_one"

            def consume(self, state: str) -> bool:
                return False

        oauth_flow = OAuthFlow(
            settings=OAuthSettings(
                client_id="111.222",
                client_secret="xxx",
                scopes=["chat:write", "commands"],
                state_store=MyOAuthStateStore(),
            )
        )
        state = oauth_flow.issue_new_state(None)
        req = BoltRequest(
            body="",
            query=f"code=foo&state={state}",
            headers={"cookie": [f"{oauth_flow.settings.state_cookie_name}={state}"]},
        )
        resp = oauth_flow.handle_callback(req)
        assert resp.status == 401

    def test_handle_callback_no_state_validation(self):
        oauth_flow = OAuthFlow(
            client=WebClient(base_url=self.mock_api_server_base_url),
            settings=OAuthSettings(
                client_id="111.222",
                client_secret="xxx",
                scopes=["chat:write", "commands"],
                installation_store=FileInstallationStore(),
                state_validation_enabled=False,  # disabled
                state_store=None,
            ),
        )
        state = oauth_flow.issue_new_state(None)
        req = BoltRequest(
            body="",
            query=f"code=foo&state=invalid",
            headers={"cookie": [f"{oauth_flow.settings.state_cookie_name}={state}"]},
        )
        resp = oauth_flow.handle_callback(req)
        assert resp.status == 200

    def test_handle_callback_using_options(self):
        def success(args: SuccessArgs) -> BoltResponse:
            assert args.request is not None
            return BoltResponse(status=200, body="customized")

        def failure(args: FailureArgs) -> BoltResponse:
            assert args.request is not None
            assert args.reason is not None
            return BoltResponse(status=502, body="customized")

        oauth_flow = OAuthFlow(
            client=WebClient(base_url=self.mock_api_server_base_url),
            settings=OAuthSettings(
                client_id="111.222",
                client_secret="xxx",
                scopes=["chat:write", "commands"],
                installation_store=FileInstallationStore(),
                state_store=FileOAuthStateStore(expiration_seconds=120),
                callback_options=CallbackOptions(success=success, failure=failure),
            ),
        )
        state = oauth_flow.issue_new_state(None)
        req = BoltRequest(
            body="",
            query=f"code=foo&state={state}",
            headers={"cookie": [f"{oauth_flow.settings.state_cookie_name}={state}"]},
        )
        resp = oauth_flow.handle_callback(req)
        assert resp.status == 200
        assert resp.body == "customized"

        state = oauth_flow.issue_new_state(None)
        req = BoltRequest(
            body="",
            query=f"code=foo&state=invalid",
            headers={"cookie": [f"{oauth_flow.settings.state_cookie_name}={state}"]},
        )
        resp = oauth_flow.handle_callback(req)
        assert resp.status == 502
        assert resp.body == "customized"
