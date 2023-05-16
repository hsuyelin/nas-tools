import json
from time import time
from urllib.parse import quote

from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier

from slack_bolt import BoltRequest, BoltResponse
from slack_bolt.app import App
from slack_bolt.error import BoltUnhandledRequestError
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestErrorHandler:
    signing_secret = "secret"
    valid_token = "xoxb-valid"
    mock_api_server_base_url = "http://localhost:8888"
    signature_verifier = SignatureVerifier(signing_secret)
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

    # ----------------
    #  utilities
    # ----------------

    def generate_signature(self, body: str, timestamp: str):
        return self.signature_verifier.generate_signature(
            body=body,
            timestamp=timestamp,
        )

    def build_headers(self, timestamp: str, body: str):
        return {
            "content-type": ["application/x-www-form-urlencoded"],
            "x-slack-signature": [self.generate_signature(body, timestamp)],
            "x-slack-request-timestamp": [timestamp],
        }

    def build_valid_request(self) -> BoltRequest:
        body = {
            "type": "block_actions",
            "user": {
                "id": "W111",
            },
            "api_app_id": "A111",
            "token": "verification_token",
            "trigger_id": "111.222.valid",
            "team": {
                "id": "T111",
            },
            "channel": {"id": "C111", "name": "test-channel"},
            "response_url": "https://hooks.slack.com/actions/T111/111/random-value",
            "actions": [
                {
                    "action_id": "a",
                    "block_id": "b",
                    "text": {"type": "plain_text", "text": "Button"},
                    "value": "click_me_123",
                    "type": "button",
                    "action_ts": "1596530385.194939",
                }
            ],
        }
        raw_body = f"payload={quote(json.dumps(body))}"
        timestamp = str(int(time()))
        return BoltRequest(body=raw_body, headers=self.build_headers(timestamp, raw_body))

    # ----------------
    #  tests
    # ----------------

    def test_default(self):
        def failing_listener():
            raise Exception("Something wrong!")

        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.action("a")(failing_listener)

        request = self.build_valid_request()
        response = app.dispatch(request)
        assert response.status == 500

    def test_custom(self):
        def error_handler(logger, payload, response):
            logger.info(payload)
            response.headers["x-test-result"] = ["1"]

        def failing_listener():
            raise Exception("Something wrong!")

        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.error(error_handler)
        app.action("a")(failing_listener)

        request = self.build_valid_request()
        response = app.dispatch(request)
        assert response.status == 500
        assert response.headers["x-test-result"] == ["1"]

    def test_process_before_response_default(self):
        def failing_listener():
            raise Exception("Something wrong!")

        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
            process_before_response=True,
        )
        app.action("a")(failing_listener)

        request = self.build_valid_request()
        response = app.dispatch(request)
        assert response.status == 500

    def test_process_before_response_custom(self):
        def error_handler(logger, payload, response):
            logger.info(payload)
            response.headers["x-test-result"] = ["1"]

        def failing_listener():
            raise Exception("Something wrong!")

        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
            process_before_response=True,
        )
        app.error(error_handler)
        app.action("a")(failing_listener)

        request = self.build_valid_request()
        response = app.dispatch(request)
        assert response.status == 500
        assert response.headers["x-test-result"] == ["1"]

    def test_unhandled_errors(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
            raise_error_for_unhandled_request=True,
        )
        response = app.dispatch(self.build_valid_request())
        assert response.status == 404
        assert response.body == '{"error": "unhandled request"}'

        @app.error
        def handle_errors(error):
            assert isinstance(error, BoltUnhandledRequestError)
            return BoltResponse(status=404, body="TODO")

        response = app.dispatch(self.build_valid_request())
        assert response.status == 404
        assert response.body == "TODO"

    def test_unhandled_errors_process_before_response(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
            raise_error_for_unhandled_request=True,
            process_before_response=True,
        )
        response = app.dispatch(self.build_valid_request())
        assert response.status == 404
        assert response.body == '{"error": "unhandled request"}'

        @app.error
        def handle_errors(error):
            assert isinstance(error, BoltUnhandledRequestError)
            return BoltResponse(status=404, body="TODO")

        response = app.dispatch(self.build_valid_request())
        assert response.status == 404
        assert response.body == "TODO"

    def test_unhandled_errors_no_next(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
            raise_error_for_unhandled_request=True,
        )

        @app.middleware
        def broken_middleware():
            pass

        response = app.dispatch(self.build_valid_request())
        assert response.status == 404
        assert response.body == '{"error": "no next() calls in middleware"}'

        @app.error
        def handle_errors(error):
            assert isinstance(error, BoltUnhandledRequestError)
            return BoltResponse(status=404, body="TODO")

        response = app.dispatch(self.build_valid_request())
        assert response.status == 404
        assert response.body == "TODO"

    def test_unhandled_errors_process_before_response_no_next(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
            raise_error_for_unhandled_request=True,
            process_before_response=True,
        )

        @app.middleware
        def broken_middleware():
            pass

        response = app.dispatch(self.build_valid_request())
        assert response.status == 404
        assert response.body == '{"error": "no next() calls in middleware"}'

        @app.error
        def handle_errors(error):
            assert isinstance(error, BoltUnhandledRequestError)
            return BoltResponse(status=404, body="TODO")

        response = app.dispatch(self.build_valid_request())
        assert response.status == 404
        assert response.body == "TODO"

    def test_global_middleware_errors(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )

        @app.middleware
        def broken_middleware(next_):
            assert next_ is not None
            raise RuntimeError("Something wrong!")

        response = app.dispatch(self.build_valid_request())
        assert response.status == 500
        assert response.body == ""

        @app.error
        def handle_errors(body, next_, error):
            assert next_ is None
            assert body is not None
            assert isinstance(error, RuntimeError)
            return BoltResponse(status=503, body="as expected")

        response = app.dispatch(self.build_valid_request())
        assert response.status == 503
        assert response.body == "as expected"
