from slack_bolt.context.respond import Respond
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)


class TestRespond:
    def setup_method(self):
        setup_mock_web_api_server(self)

    def teardown_method(self):
        cleanup_mock_web_api_server(self)

    def test_respond(self):
        response_url = "http://localhost:8888"
        respond = Respond(response_url=response_url)
        response = respond(text="Hi there!")
        assert response.status_code == 200

    def test_respond2(self):
        response_url = "http://localhost:8888"
        respond = Respond(response_url=response_url)
        response = respond({"text": "Hi there!"})
        assert response.status_code == 200

    def test_unfurl_options(self):
        response_url = "http://localhost:8888"
        respond = Respond(response_url=response_url)
        response = respond(text="Hi there!", unfurl_media=True, unfurl_links=True)
        assert response.status_code == 200
