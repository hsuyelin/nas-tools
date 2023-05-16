from slack_sdk import WebClient

from slack_bolt import BoltRequest, BoltResponse
from slack_bolt.oauth import OAuthFlow
from slack_bolt.oauth.callback_options import CallbackOptions, SuccessArgs, FailureArgs
from tests.mock_web_api_server import (
    cleanup_mock_web_api_server,
    setup_mock_web_api_server,
)


class TestOAuthFlowSQLite3:
    mock_api_server_base_url = "http://localhost:8888"

    def setup_method(self):
        setup_mock_web_api_server(self)

    def teardown_method(self):
        cleanup_mock_web_api_server(self)

    def test_instantiation(self):
        oauth_flow = OAuthFlow.sqlite3(
            database="./logs/test_db",
            client_id="111.222",
            client_secret="xxx",
            scopes=["chat:write", "commands"],
        )
        assert oauth_flow is not None
        assert oauth_flow.logger is not None
        assert oauth_flow.client is not None

    def test_handle_installation(self):
        oauth_flow = OAuthFlow.sqlite3(
            client=WebClient(base_url=self.mock_api_server_base_url),
            database="./logs/test_db",
            client_id="111.222",
            client_secret="xxx",
            scopes=["chat:write", "commands"],
        )
        req = BoltRequest(body="")
        resp = oauth_flow.handle_installation(req)
        assert resp.status == 200
        assert resp.headers.get("content-type") == ["text/html; charset=utf-8"]
        assert "https://slack.com/oauth/v2/authorize?state=" in resp.body

    def test_handle_callback(self):
        oauth_flow = OAuthFlow.sqlite3(
            client=WebClient(base_url=self.mock_api_server_base_url),
            database="./logs/test_db",
            client_id="111.222",
            client_secret="xxx",
            scopes=["chat:write", "commands"],
            success_url="https://www.example.com/completion",
            failure_url="https://www.example.com/failure",
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

    def test_handle_callback_invalid_state(self):
        oauth_flow = OAuthFlow.sqlite3(
            client=WebClient(base_url=self.mock_api_server_base_url),
            database="./logs/test_db",
            client_id="111.222",
            client_secret="xxx",
            scopes=["chat:write", "commands"],
        )
        state = oauth_flow.issue_new_state(None)
        req = BoltRequest(
            body="",
            query=f"code=foo&state=invalid",
            headers={"cookie": [f"{oauth_flow.settings.state_cookie_name}={state}"]},
        )
        resp = oauth_flow.handle_callback(req)
        assert resp.status == 400

    def test_handle_callback_using_options(self):
        def success(args: SuccessArgs) -> BoltResponse:
            assert args.request is not None
            return BoltResponse(status=200, body="customized")

        def failure(args: FailureArgs) -> BoltResponse:
            assert args.request is not None
            assert args.reason is not None
            return BoltResponse(status=502, body="customized")

        oauth_flow = OAuthFlow.sqlite3(
            client=WebClient(base_url=self.mock_api_server_base_url),
            database="./logs/test_db",
            client_id="111.222",
            client_secret="xxx",
            scopes=["chat:write", "commands"],
            callback_options=CallbackOptions(success=success, failure=failure),
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
