import json
from time import time
from urllib.parse import quote

from slack_sdk.signature import SignatureVerifier
from slack_sdk.web import WebClient
from tornado.httpclient import HTTPRequest, HTTPResponse
from tornado.testing import AsyncHTTPTestCase, gen_test
from tornado.web import Application

from slack_bolt.adapter.tornado import SlackEventsHandler
from slack_bolt.app import App
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
    assert_auth_test_count,
)
from tests.utils import remove_os_env_temporarily, restore_os_env

signing_secret = "secret"
valid_token = "xoxb-valid"
mock_api_server_base_url = "http://localhost:8888"


def event_handler():
    pass


def shortcut_handler(ack):
    ack()


def command_handler(ack):
    ack()


class TestTornado(AsyncHTTPTestCase):
    signature_verifier = SignatureVerifier(signing_secret)

    def setUp(self):
        self.old_os_env = remove_os_env_temporarily()
        setup_mock_web_api_server(self)

        web_client = WebClient(
            token=valid_token,
            base_url=mock_api_server_base_url,
        )
        self.app = App(
            client=web_client,
            signing_secret=signing_secret,
        )
        self.app.event("app_mention")(event_handler)
        self.app.shortcut("test-shortcut")(shortcut_handler)
        self.app.command("/hello-world")(command_handler)

        AsyncHTTPTestCase.setUp(self)

    def tearDown(self):
        AsyncHTTPTestCase.tearDown(self)
        cleanup_mock_web_api_server(self)
        restore_os_env(self.old_os_env)

    def get_app(self):
        return Application([("/slack/events", SlackEventsHandler, dict(app=self.app))])

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

    @gen_test
    async def test_events(self):
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

        request = HTTPRequest(
            url=self.get_url("/slack/events"),
            method="POST",
            body=body,
            headers=self.build_headers(timestamp, body),
        )
        response: HTTPResponse = await self.http_client.fetch(request)
        assert response.code == 200
        assert_auth_test_count(self, 1)

    @gen_test
    async def test_shortcuts(self):
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

        request = HTTPRequest(
            url=self.get_url("/slack/events"),
            method="POST",
            body=body,
            headers=self.build_headers(timestamp, body),
        )
        response: HTTPResponse = await self.http_client.fetch(request)
        assert response.code == 200
        assert_auth_test_count(self, 1)

    @gen_test
    async def test_commands(self):
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

        request = HTTPRequest(
            url=self.get_url("/slack/events"),
            method="POST",
            body=body,
            headers=self.build_headers(timestamp, body),
        )
        response: HTTPResponse = await self.http_client.fetch(request)
        assert response.code == 200
        assert_auth_test_count(self, 1)
