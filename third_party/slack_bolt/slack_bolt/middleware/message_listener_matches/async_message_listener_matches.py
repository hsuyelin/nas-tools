import re
from typing import Callable, Awaitable, Union, Pattern

from slack_bolt.request.async_request import AsyncBoltRequest
from slack_bolt.response import BoltResponse
from slack_bolt.middleware.async_middleware import AsyncMiddleware


class AsyncMessageListenerMatches(AsyncMiddleware):
    def __init__(self, keyword: Union[str, Pattern]):
        """Captures matched keywords and saves the values in context."""
        self.keyword = keyword

    async def async_process(
        self,
        *,
        req: AsyncBoltRequest,
        resp: BoltResponse,
        # As this method is not supposed to be invoked by bolt-python users,
        # the naming conflict with the built-in one affects
        # only the internals of this method
        next: Callable[[], Awaitable[BoltResponse]],
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
                return await next()

        # As the text doesn't match, skip running the listener
        return resp
