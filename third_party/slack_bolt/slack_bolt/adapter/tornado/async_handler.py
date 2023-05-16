from tornado.httputil import HTTPServerRequest
from tornado.web import RequestHandler

from slack_bolt.async_app import AsyncApp
from slack_bolt.oauth.async_oauth_flow import AsyncOAuthFlow
from slack_bolt.request.async_request import AsyncBoltRequest
from slack_bolt.response import BoltResponse
from .handler import set_response


class AsyncSlackEventsHandler(RequestHandler):
    def initialize(self, app: AsyncApp):  # type: ignore
        self.app = app

    async def post(self):
        bolt_resp: BoltResponse = await self.app.async_dispatch(to_async_bolt_request(self.request))
        set_response(self, bolt_resp)
        return


class AsyncSlackOAuthHandler(RequestHandler):
    def initialize(self, app: AsyncApp):  # type: ignore
        self.app = app

    async def get(self):
        if self.app.oauth_flow is not None:  # type: ignore
            oauth_flow: AsyncOAuthFlow = self.app.oauth_flow  # type: ignore
            if self.request.path == oauth_flow.install_path:
                bolt_resp = await oauth_flow.handle_installation(to_async_bolt_request(self.request))
                set_response(self, bolt_resp)
                return
            elif self.request.path == oauth_flow.redirect_uri_path:
                bolt_resp = await oauth_flow.handle_callback(to_async_bolt_request(self.request))
                set_response(self, bolt_resp)
                return
        self.set_status(404)


def to_async_bolt_request(req: HTTPServerRequest) -> AsyncBoltRequest:
    return AsyncBoltRequest(
        body=req.body.decode("utf-8") if req.body else "",
        query=req.query,
        headers=req.headers,
    )
