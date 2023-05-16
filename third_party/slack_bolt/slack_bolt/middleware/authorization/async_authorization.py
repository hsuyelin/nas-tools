from abc import ABC

from slack_bolt.middleware.async_middleware import AsyncMiddleware


class AsyncAuthorization(AsyncMiddleware, ABC):
    pass
