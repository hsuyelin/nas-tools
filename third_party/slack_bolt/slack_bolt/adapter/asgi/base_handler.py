from typing import Callable, Dict

from .http_request import AsgiHttpRequest
from .http_response import AsgiHttpResponse
from .utils import scope_type

from slack_bolt import App

from slack_bolt.response import BoltResponse

"""
This handler implements the ASGI standard found here https://asgi.readthedocs.io/en/latest/specs/index.html
"""


class BaseSlackRequestHandler:
    app: App  # type: ignore
    path: str

    async def dispatch(self, request: AsgiHttpRequest) -> BoltResponse:
        """Dispatches a request to the Bolt App"""
        raise NotImplementedError

    async def handle_installation(self, request: AsgiHttpRequest) -> BoltResponse:
        """Handles installation of the OAuthFlow"""
        raise NotImplementedError

    async def handle_callback(self, request: AsgiHttpRequest) -> BoltResponse:
        """Handles the callback of the OAuthFlow"""
        raise NotImplementedError

    async def _get_http_response(self, method: str, path: str, request: AsgiHttpRequest) -> AsgiHttpResponse:
        if method == "GET":
            if self.app.oauth_flow is not None:
                if path == self.app.oauth_flow.install_path:
                    bolt_response: BoltResponse = await self.handle_installation(request)
                    return AsgiHttpResponse(
                        status=bolt_response.status, headers=bolt_response.headers, body=bolt_response.body
                    )
                if path == self.app.oauth_flow.redirect_uri_path:
                    bolt_response: BoltResponse = await self.handle_callback(request)
                    return AsgiHttpResponse(
                        status=bolt_response.status, headers=bolt_response.headers, body=bolt_response.body
                    )
        if method == "POST" and path == self.path:
            bolt_response: BoltResponse = await self.dispatch(request)
            return AsgiHttpResponse(status=bolt_response.status, headers=bolt_response.headers, body=bolt_response.body)
        return AsgiHttpResponse(status=404, headers={"content-type": ["text/plain;charset=utf-8"]}, body="Not Found")

    async def _handle_lifespan(self, receive: Callable) -> Dict[str, str]:
        while True:
            lifespan = await receive()
            if lifespan["type"] == "lifespan.startup":
                """Do something before startup"""
                return {"type": "lifespan.startup.complete"}
            if lifespan["type"] == "lifespan.shutdown":
                """Do something before shutdown"""
                return {"type": "lifespan.shutdown.complete"}

    async def __call__(self, scope: scope_type, receive: Callable, send: Callable) -> None:
        if scope["type"] == "http":
            response: AsgiHttpResponse = await self._get_http_response(
                scope["method"], scope["path"], AsgiHttpRequest(scope, receive)
            )
            await send(response.get_response_start())
            await send(response.get_response_body())
            return
        if scope["type"] == "lifespan":
            await send(await self._handle_lifespan(receive))
            return
        raise TypeError(f"Unsupported scope type: {scope['type']}")
