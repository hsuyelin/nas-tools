from slack_bolt import BoltRequest
from slack_bolt.error import BoltUnhandledRequestError


class TestErrors:
    def setup_method(self):
        pass

    def teardown_method(self):
        pass

    def test_say(self):
        request = BoltRequest(body="foo=bar")
        exception = BoltUnhandledRequestError(
            request=request,
            current_response={},
            last_global_middleware_name="last_middleware",
        )
        assert str(exception) == "unhandled request error"
