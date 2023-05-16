import json
from time import time
from urllib.parse import quote

from moto import mock_lambda
from slack_sdk.signature import SignatureVerifier
from slack_sdk.web import WebClient
from slack_sdk.oauth import OAuthStateStore

from slack_bolt.adapter.aws_lambda import SlackRequestHandler
from slack_bolt.adapter.aws_lambda.handler import not_found
from slack_bolt.adapter.aws_lambda.internals import _first_value
from slack_bolt.app import App
from slack_bolt.oauth.oauth_settings import OAuthSettings
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
    assert_auth_test_count,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class LambdaContext:
    function_name: str

    def __init__(self, function_name: str):
        self.function_name = function_name
        self.invoked_function_arn = f"arn:aws:lambda:us-east-1:account-id:function:{self.function_name}"


class TestAWSLambda:
    signing_secret = "secret"
    valid_token = "xoxb-valid"
    mock_api_server_base_url = "http://localhost:8888"
    signature_verifier = SignatureVerifier(signing_secret)
    web_client = WebClient(
        token=valid_token,
        base_url=mock_api_server_base_url,
    )

    context = LambdaContext(function_name="test-function")

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
            "content-type": [content_type],
            "x-slack-signature": [self.generate_signature(body, timestamp)],
            "x-slack-request-timestamp": [timestamp],
        }

    def test_not_found(self):
        response = not_found()
        assert response["statusCode"] == 404

    def test_first_value(self):
        assert _first_value({"foo": [1, 2, 3]}, "foo") == 1
        assert _first_value({"foo": []}, "foo") is None
        assert _first_value({}, "foo") is None

    @mock_lambda
    def test_clear_all_log_handlers(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        handler = SlackRequestHandler(app)
        handler.clear_all_log_handlers()

    @mock_lambda
    def test_events(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )

        def event_handler():
            pass

        app.event("app_mention")(event_handler)

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
        event = {
            "body": body,
            "queryStringParameters": {},
            "headers": self.build_headers(timestamp, body),
            "requestContext": {"http": {"method": "POST"}},
            "isBase64Encoded": False,
        }
        response = SlackRequestHandler(app).handle(event, self.context)
        assert response["statusCode"] == 200
        assert_auth_test_count(self, 1)

        event = {
            "body": body,
            "queryStringParameters": {},
            "headers": self.build_headers(timestamp, body),
            "requestContext": {"httpMethod": "POST"},
            "isBase64Encoded": False,
        }
        response = SlackRequestHandler(app).handle(event, self.context)
        assert response["statusCode"] == 200
        assert_auth_test_count(self, 1)

    @mock_lambda
    def test_shortcuts(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )

        def shortcut_handler(ack):
            ack()

        app.shortcut("test-shortcut")(shortcut_handler)

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
        event = {
            "body": body,
            "queryStringParameters": {},
            "headers": self.build_headers(timestamp, body),
            "requestContext": {"http": {"method": "POST"}},
            "isBase64Encoded": False,
        }
        response = SlackRequestHandler(app).handle(event, self.context)
        assert response["statusCode"] == 200
        assert_auth_test_count(self, 1)

        event = {
            "body": body,
            "queryStringParameters": {},
            "headers": self.build_headers(timestamp, body),
            "requestContext": {"httpMethod": "POST"},
            "isBase64Encoded": False,
        }
        response = SlackRequestHandler(app).handle(event, self.context)
        assert response["statusCode"] == 200
        assert_auth_test_count(self, 1)

    @mock_lambda
    def test_commands(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )

        def command_handler(ack):
            ack()

        app.command("/hello-world")(command_handler)

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
        event = {
            "body": body,
            "queryStringParameters": {},
            "headers": self.build_headers(timestamp, body),
            "requestContext": {"http": {"method": "POST"}},
            "isBase64Encoded": False,
        }
        response = SlackRequestHandler(app).handle(event, self.context)
        assert response["statusCode"] == 200
        assert_auth_test_count(self, 1)

        event = {
            "body": body,
            "queryStringParameters": {},
            "headers": self.build_headers(timestamp, body),
            "requestContext": {"httpMethod": "POST"},
            "isBase64Encoded": False,
        }
        response = SlackRequestHandler(app).handle(event, self.context)
        assert response["statusCode"] == 200
        assert_auth_test_count(self, 1)

    @mock_lambda
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
        headers = self.build_headers(timestamp, body)
        headers["x-slack-bolt-lazy-only"] = "1"
        headers["x-slack-bolt-lazy-function-name"] = "say_it"
        event = {
            "body": body,
            "queryStringParameters": {},
            "headers": headers,
            "requestContext": {"http": {"method": "NONE"}},
            "isBase64Encoded": False,
        }
        response = SlackRequestHandler(app).handle(event, self.context)
        assert response["statusCode"] == 200
        assert_auth_test_count(self, 1)
        assert self.mock_received_requests["/chat.postMessage"] == 1

    @mock_lambda
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

        event = {
            "body": "",
            "queryStringParameters": {},
            "headers": {},
            "requestContext": {"http": {"method": "GET"}},
            "isBase64Encoded": False,
        }
        response = SlackRequestHandler(app).handle(event, self.context)
        assert response["statusCode"] == 200
        assert response["headers"]["content-type"] == "text/html; charset=utf-8"
        assert response.get("body") is not None

        event = {
            "body": "",
            "queryStringParameters": {},
            "headers": {},
            "requestContext": {"httpMethod": "GET"},
            "isBase64Encoded": False,
        }
        response = SlackRequestHandler(app).handle(event, self.context)
        assert response["statusCode"] == 200
        assert response["headers"]["content-type"] == "text/html; charset=utf-8"
        assert "https://slack.com/oauth/v2/authorize?state=" in response.get("body")

    @mock_lambda
    def test_oauth_redirect(self):
        class TestStateStore(OAuthStateStore):
            def consume(self, state: str) -> bool:
                return state == "uuid4-value"

        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
            oauth_settings=OAuthSettings(
                client_id="111.111",
                client_secret="xxx",
                scopes=["chat:write", "commands"],
                state_store=TestStateStore(),
            ),
        )

        event = {
            "body": "",
            "queryStringParameters": {"code": "1234567890", "state": "uuid4-value"},
            "headers": {},
            "cookies": ["slack-app-oauth-state=uuid4-value"],
            "requestContext": {"http": {"method": "GET"}},
            "isBase64Encoded": False,
        }
        response = SlackRequestHandler(app).handle(event, self.context)
        assert response["statusCode"] == 200
        assert response["headers"]["content-type"] == "text/html; charset=utf-8"
        assert response.get("body") is not None

        event = {
            "body": "",
            "queryStringParameters": {"code": "1234567890", "state": "uuid4-value"},
            "headers": {},
            "multiValueHeaders": {"Cookie": ["slack-app-oauth-state=uuid4-value"]},
            "requestContext": {"httpMethod": "GET"},
            "isBase64Encoded": False,
        }
        response = SlackRequestHandler(app).handle(event, self.context)
        assert response["statusCode"] == 200
        assert response["headers"]["content-type"] == "text/html; charset=utf-8"
        assert response.get("body") is not None
