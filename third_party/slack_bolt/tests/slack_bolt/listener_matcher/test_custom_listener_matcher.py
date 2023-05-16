from slack_bolt import BoltRequest, BoltResponse, CustomListenerMatcher
from slack_bolt.listener_matcher import ListenerMatcher


def func(body, request, response, dummy):
    assert body is not None
    assert request is not None
    assert response is not None
    assert dummy is None
    return body["result"]


class TestCustomListenerMatcher:
    def setup_method(self):
        pass

    def teardown_method(self):
        pass

    def test_instantiation(self):
        matcher: ListenerMatcher = CustomListenerMatcher(
            app_name="foo",
            func=func,
        )
        resp = BoltResponse(status=201)

        req = BoltRequest(body='payload={"result":true}')
        result = matcher.matches(req, resp)
        assert result is True

        req = BoltRequest(body='payload={"result":false}')
        result = matcher.matches(req, resp)
        assert result is False
