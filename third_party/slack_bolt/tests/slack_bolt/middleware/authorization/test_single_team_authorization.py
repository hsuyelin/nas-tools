from slack_sdk import WebClient

from slack_bolt.middleware import SingleTeamAuthorization
from slack_bolt.middleware.authorization.internals import _build_error_text
from slack_bolt.request import BoltRequest
from slack_bolt.response import BoltResponse
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)


def next():
    return BoltResponse(status=200)


class TestSingleTeamAuthorization:
    mock_api_server_base_url = "http://localhost:8888"

    def setup_method(self):
        setup_mock_web_api_server(self)

    def teardown_method(self):
        cleanup_mock_web_api_server(self)

    def test_success_pattern(self):
        authorization = SingleTeamAuthorization(auth_test_result={})
        req = BoltRequest(body="payload={}", headers={})
        req.context["client"] = WebClient(base_url=self.mock_api_server_base_url, token="xoxb-valid")
        resp = BoltResponse(status=404)

        resp = authorization.process(req=req, resp=resp, next=next)

        assert resp.status == 200
        assert resp.body == ""

    def test_failure_pattern(self):
        authorization = SingleTeamAuthorization(auth_test_result={})
        req = BoltRequest(body="payload={}", headers={})
        req.context["client"] = WebClient(base_url=self.mock_api_server_base_url, token="dummy")
        resp = BoltResponse(status=404)

        resp = authorization.process(req=req, resp=resp, next=next)

        assert resp.status == 200
        assert resp.body == _build_error_text()
