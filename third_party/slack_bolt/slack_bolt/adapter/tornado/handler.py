from datetime import datetime  # type: ignore

from tornado.httputil import HTTPServerRequest
from tornado.web import RequestHandler

from slack_bolt.app import App
from slack_bolt.oauth import OAuthFlow
from slack_bolt.request import BoltRequest
from slack_bolt.response import BoltResponse


class SlackEventsHandler(RequestHandler):
    def initialize(self, app: App):  # type: ignore
        self.app = app

    def post(self):
        bolt_resp: BoltResponse = self.app.dispatch(to_bolt_request(self.request))
        set_response(self, bolt_resp)
        return


class SlackOAuthHandler(RequestHandler):
    def initialize(self, app: App):  # type: ignore
        self.app = app

    def get(self):
        if self.app.oauth_flow is not None:  # type: ignore
            oauth_flow: OAuthFlow = self.app.oauth_flow  # type: ignore
            if self.request.path == oauth_flow.install_path:
                bolt_resp = oauth_flow.handle_installation(to_bolt_request(self.request))
                set_response(self, bolt_resp)
                return
            elif self.request.path == oauth_flow.redirect_uri_path:
                bolt_resp = oauth_flow.handle_callback(to_bolt_request(self.request))
                set_response(self, bolt_resp)
                return
        self.set_status(404)


def to_bolt_request(req: HTTPServerRequest) -> BoltRequest:
    return BoltRequest(
        body=req.body.decode("utf-8") if req.body else "",
        query=req.query,
        headers=req.headers,
    )


def set_response(self, bolt_resp) -> None:
    self.set_status(bolt_resp.status)
    self.write(bolt_resp.body)
    for name, value in bolt_resp.first_headers_without_set_cookie().items():
        self.set_header(name, value)
    for cookie in bolt_resp.cookies():
        for name, c in cookie.items():
            expire_value = c.get("expires")
            expire = datetime.strptime(expire_value, "%a, %d %b %Y %H:%M:%S %Z") if expire_value else None
            self.set_cookie(
                name=name,
                value=c.value,
                max_age=c.get("max-age"),
                expires=expire,
                path=c.get("path"),
                domain=c.get("domain"),
                secure=True,
                httponly=True,
            )
