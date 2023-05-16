import json
import os
from time import time
from typing import Dict, Any
from urllib.parse import quote
from unittest import mock

from chalice import Chalice, Response
from chalice.app import Request
from chalice.config import Config
from chalice.local import LocalGateway
from chalice.test import Client
from slack_sdk.signature import SignatureVerifier
from slack_sdk.web import WebClient

from slack_bolt.adapter.aws_lambda.chalice_handler import (
    ChaliceSlackRequestHandler,
    not_found,
)

from slack_bolt.app import App
from slack_bolt.oauth.oauth_settings import OAuthSettings
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
    assert_auth_test_count,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestAwsChalice:
    signing_secret = "secret"
    valid_token = "xoxb-valid"
    mock_api_server_base_url = "http://localhost:8888"
    signature_verifier = SignatureVerifier(signing_secret)
    web_client = WebClient(token=valid_token, base_url=mock_api_server_base_url)

    def setup_method(self):
        self.old_os_env = remove_os_env_temporarily()
        setup_mock_web_api_server(self)

    def teardown_method(self):
        cleanup_mock_web_api_server(self)
        restore_os_env(self.old_os_env)

    def generate_signature(self, body: str, timestamp: str):
        return self.signature_verifier.generate_signature(
            body=body,
            timestamp=timestamp,
        )

    def build_headers(self, timestamp: str, body: str):
        content_type = "application/json" if body.startswith("{") else "application/x-www-form-urlencoded"
        return {
            "content-type": content_type,
            "x-slack-signature": self.generate_signature(body, timestamp),
            "x-slack-request-timestamp": timestamp,
        }

    def test_not_found(self):
        response = not_found()
        assert response.status_code == 404

    def test_events(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )

        @app.event("app_mention")
        def event_handler():
            pass

        input = {
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
        timestamp, body = str(int(time())), json.dumps(input)

        chalice_app = Chalice(app_name="bolt-python-chalice")
        slack_handler = ChaliceSlackRequestHandler(app=app, chalice=chalice_app)

        @chalice_app.route(
            "/slack/events",
            methods=["POST"],
            content_types=["application/x-www-form-urlencoded", "application/json"],
        )
        def events() -> Response:
            return slack_handler.handle(chalice_app.current_request)

        response: Dict[str, Any] = LocalGateway(chalice_app, Config()).handle_request(
            method="POST",
            path="/slack/events",
            body=body,
            headers=self.build_headers(timestamp, body),
        )
        assert response["statusCode"] == 200
        assert_auth_test_count(self, 1)

    def test_shortcuts(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )

        @app.shortcut("test-shortcut")
        def shortcut_handler(ack):
            ack()

        input = {
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

        timestamp, body = str(int(time())), f"payload={quote(json.dumps(input))}"

        chalice_app = Chalice(app_name="bolt-python-chalice")
        slack_handler = ChaliceSlackRequestHandler(app=app, chalice=chalice_app)

        @chalice_app.route(
            "/slack/events",
            methods=["POST"],
            content_types=["application/x-www-form-urlencoded", "application/json"],
        )
        def events() -> Response:
            return slack_handler.handle(chalice_app.current_request)

        response: Dict[str, Any] = LocalGateway(chalice_app, Config()).handle_request(
            method="POST",
            path="/slack/events",
            body=body,
            headers=self.build_headers(timestamp, body),
        )
        assert response["statusCode"] == 200
        assert_auth_test_count(self, 1)

    def test_commands(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )

        @app.command("/hello-world")
        def command_handler(ack):
            ack()

        input = (
            "token=verification_token"
            "&team_id=T111"
            "&team_domain=test-domain"
            "&channel_id=C111"
            "&channel_name=random"
            "&user_id=W111"
            "&user_name=primary-owner"
            "&command=%2Fhello-world"
            "&text=Hi"
            "&enterprise_id=E111"
            "&enterprise_name=Org+Name"
            "&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT111%2F111%2Fxxxxx"
            "&trigger_id=111.111.xxx"
        )
        timestamp, body = str(int(time())), input

        chalice_app = Chalice(app_name="bolt-python-chalice")
        slack_handler = ChaliceSlackRequestHandler(app=app, chalice=chalice_app)

        @chalice_app.route(
            "/slack/events",
            methods=["POST"],
            content_types=["application/x-www-form-urlencoded", "application/json"],
        )
        def events() -> Response:
            return slack_handler.handle(chalice_app.current_request)

        response: Dict[str, Any] = LocalGateway(chalice_app, Config()).handle_request(
            method="POST",
            path="/slack/events",
            body=body,
            headers=self.build_headers(timestamp, body),
        )
        assert response["statusCode"] == 200
        assert_auth_test_count(self, 1)

    def test_lazy_listeners(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )

        def command_handler(ack):
            ack()

        def say_it(say):
            say("Done!")

        app.command("/hello-world")(ack=command_handler, lazy=[say_it])

        input = (
            "token=verification_token"
            "&team_id=T111"
            "&team_domain=test-domain"
            "&channel_id=C111"
            "&channel_name=random"
            "&user_id=W111"
            "&user_name=primary-owner"
            "&command=%2Fhello-world"
            "&text=Hi"
            "&enterprise_id=E111"
            "&enterprise_name=Org+Name"
            "&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT111%2F111%2Fxxxxx"
            "&trigger_id=111.111.xxx"
        )
        timestamp, body = str(int(time())), input

        chalice_app = Chalice(app_name="bolt-python-chalice")
        slack_handler = ChaliceSlackRequestHandler(app=app, chalice=chalice_app)

        headers = self.build_headers(timestamp, body)
        headers["x-slack-bolt-lazy-only"] = "1"
        headers["x-slack-bolt-lazy-function-name"] = "say_it"

        request: Request = Request(
            {
                "requestContext": {
                    "httpMethod": "NONE",
                    "resourcePath": "/slack/events",
                },
                "multiValueQueryStringParameters": {},
                "pathParameters": {},
                "context": {},
                "stageVariables": None,
                "isBase64Encoded": False,
                "body": body,
                "headers": headers,
            }
        )
        response: Response = slack_handler.handle(request)
        assert response.status_code == 200
        assert_auth_test_count(self, 1)
        assert self.mock_received_requests["/chat.postMessage"] == 1

    def test_lazy_listeners_cli(self):
        with mock.patch.dict(os.environ, {"AWS_CHALICE_CLI_MODE": "true"}):
            assert os.environ.get("AWS_CHALICE_CLI_MODE") == "true"
            app = App(
                client=self.web_client,
                signing_secret=self.signing_secret,
                process_before_response=True,
            )

            def command_handler(ack):
                ack()

            def say_it(say):
                say("Done!")

            app.command("/hello-world")(ack=command_handler, lazy=[say_it])

            input = (
                "token=verification_token"
                "&team_id=T111"
                "&team_domain=test-domain"
                "&channel_id=C111"
                "&channel_name=random"
                "&user_id=W111"
                "&user_name=primary-owner"
                "&command=%2Fhello-world"
                "&text=Hi"
                "&enterprise_id=E111"
                "&enterprise_name=Org+Name"
                "&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT111%2F111%2Fxxxxx"
                "&trigger_id=111.111.xxx"
            )
            timestamp, body = str(int(time())), input

            chalice_app = Chalice(app_name="bolt-python-chalice")
            slack_handler = ChaliceSlackRequestHandler(app=app, chalice=chalice_app)

            @chalice_app.route(
                "/slack/events",
                methods=["POST"],
                content_types=["application/x-www-form-urlencoded", "application/json"],
            )
            def events() -> Response:
                return slack_handler.handle(chalice_app.current_request)

            headers = self.build_headers(timestamp, body)
            client = Client(chalice_app)
            response = client.http.post("/slack/events", headers=headers, body=body)

            assert response.status_code == 200, f"Failed request: {response.body}"
            assert_auth_test_count(self, 1)
            assert self.mock_received_requests["/chat.postMessage"] == 1

    @mock.patch(
        "slack_bolt.adapter.aws_lambda.chalice_lazy_listener_runner.boto3",
        autospec=True,
    )
    def test_lazy_listeners_non_cli(self, mock_boto3):
        with mock.patch.dict(os.environ, {"AWS_CHALICE_CLI_MODE": "false"}):
            assert os.environ.get("AWS_CHALICE_CLI_MODE") == "false"

            mock_lambda = mock.MagicMock()  # mock of boto3.client('lambda')
            mock_boto3.client.return_value = mock_lambda
            app = App(
                client=self.web_client,
                signing_secret=self.signing_secret,
                process_before_response=True,
            )

            def command_handler(ack):
                ack()

            def say_it(say):
                say("Done!")

            app.command("/hello-world")(ack=command_handler, lazy=[say_it])

            input = (
                "token=verification_token"
                "&team_id=T111"
                "&team_domain=test-domain"
                "&channel_id=C111"
                "&channel_name=random"
                "&user_id=W111"
                "&user_name=primary-owner"
                "&command=%2Fhello-world"
                "&text=Hi"
                "&enterprise_id=E111"
                "&enterprise_name=Org+Name"
                "&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT111%2F111%2Fxxxxx"
                "&trigger_id=111.111.xxx"
            )
            timestamp, body = str(int(time())), input

            chalice_app = Chalice(app_name="bolt-python-chalice")

            slack_handler = ChaliceSlackRequestHandler(app=app, chalice=chalice_app)

            @chalice_app.route(
                "/slack/events",
                methods=["POST"],
                content_types=["application/x-www-form-urlencoded", "application/json"],
            )
            def events() -> Response:
                return slack_handler.handle(chalice_app.current_request)

            headers = self.build_headers(timestamp, body)
            client = Client(chalice_app)
            response = client.http.post("/slack/events", headers=headers, body=body)
            assert response
            assert mock_lambda.invoke.called

    def test_oauth(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
            oauth_settings=OAuthSettings(
                client_id="111.111",
                client_secret="xxx",
                scopes=["chat:write", "commands"],
            ),
        )

        chalice_app = Chalice(app_name="bolt-python-chalice")
        slack_handler = ChaliceSlackRequestHandler(app=app, chalice=chalice_app)

        @chalice_app.route("/slack/install", methods=["GET"])
        def install() -> Response:
            return slack_handler.handle(chalice_app.current_request)

        response: Dict[str, Any] = LocalGateway(chalice_app, Config()).handle_request(
            method="GET", path="/slack/install", body="", headers={}
        )
        assert response["statusCode"] == 200
        assert response["headers"]["content-type"] == "text/html; charset=utf-8"
        assert "https://slack.com/oauth/v2/authorize?state=" in response.get("body")
