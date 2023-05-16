import re
from typing import Callable, Pattern, Union

from slack_bolt.request import BoltRequest
from slack_bolt.response import BoltResponse
from slack_bolt.middleware.middleware import Middleware


class MessageListenerMatches(Middleware):  # type: ignore
    def __init__(self, keyword: Union[str, Pattern]):
        """Captures matched keywords and saves the values in context."""
        self.keyword = keyword

    def process(
        self,
        *,
        req: BoltRequest,
        resp: BoltResponse,
        # As this method is not supposed to be invoked by bolt-python users,
        # the naming conflict with the built-in one affects
        # only the internals of this method
        next: Callable[[], BoltResponse],
    ) -> BoltResponse:
        text = req.body.get("event", {}).get("text", "")
        if text:
            m = re.findall(self.keyword, text)
            if m is not None and m != []:
                if type(m[0]) is not tuple:
                    m = tuple(m)
                else:
                    m = m[0]
                req.context["matches"] = m  # tuple or list
                return next()

        # As the text doesn't match, skip running the listener
        return resp
