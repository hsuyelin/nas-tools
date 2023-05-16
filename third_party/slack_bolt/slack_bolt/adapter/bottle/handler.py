from bottle import Request, Response

from slack_bolt.app import App
from slack_bolt.oauth import OAuthFlow
from slack_bolt.request import BoltRequest
from slack_bolt.response import BoltResponse


def to_bolt_request(req: Request) -> BoltRequest:
    body = req.body.read()
    if isinstance(body, bytes):
        body = body.decode("utf-8")
    return BoltRequest(
        body=body,
        query=req.query_string,
        headers=req.headers,
    )


def set_response(bolt_resp: BoltResponse, resp: Response) -> None:
    resp.status = bolt_resp.status
    for k, values in bolt_resp.headers.items():
        for v in values:
            resp.add_header(k, v)


class SlackRequestHandler:
    def __init__(self, app: App):  # type: ignore
        self.app = app

    def handle(self, req: Request, resp: Response) -> str:
        if req.method == "GET":
            if self.app.oauth_flow is not None:
                oauth_flow: OAuthFlow = self.app.oauth_flow
                if req.path == oauth_flow.install_path:
                    bolt_resp = oauth_flow.handle_installation(to_bolt_request(req))
                    set_response(bolt_resp, resp)
                    return bolt_resp.body or ""
                elif req.path == oauth_flow.redirect_uri_path:
                    bolt_resp = oauth_flow.handle_callback(to_bolt_request(req))
                    set_response(bolt_resp, resp)
                    return bolt_resp.body or ""
        elif req.method == "POST":
            bolt_resp: BoltResponse = self.app.dispatch(to_bolt_request(req))
            set_response(bolt_resp, resp)
            return bolt_resp.body or ""

        resp.status = 404
        return "Not Found"
