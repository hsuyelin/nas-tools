import logging

from slack_bolt import BoltRequest
from slack_bolt.listener.listener_start_handler import (
    CustomListenerStartHandler,
)


class TestListenerStartHandler:
    def test_handler(self):
        result = {"called": False}

        def f():
            result["called"] = True

        handler = CustomListenerStartHandler(
            logger=logging.getLogger(__name__),
            func=f,
        )
        request = BoltRequest(
            body="{}",
            query={},
            headers={"content-type": ["application/json"]},
            context={},
        )
        handler.handle(request, None)
        assert result["called"] is True
