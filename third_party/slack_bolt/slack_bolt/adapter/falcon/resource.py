from datetime import datetime  # type: ignore
from http import HTTPStatus

from falcon import Request, Response, version as falcon_version

from slack_bolt import BoltResponse
from slack_bolt.app import App
from slack_bolt.oauth import OAuthFlow
from slack_bolt.request import BoltRequest


class SlackAppResource:
    """
    from slack_bolt import App
    app = App()

    import falcon
    api = application = falcon.API()
    api.add_route("/slack/events", SlackAppResource(app))
    """

    def __init__(self, app: App):  # type: ignore
        self.app = app

    def on_get(self, req: Request, resp: Response):
        if self.app.oauth_flow is not None:
            oauth_flow: OAuthFlow = self.app.oauth_flow
            if req.path == oauth_flow.install_path:
                bolt_resp = oauth_flow.handle_installation(self._to_bolt_request(req))
                self._write_response(bolt_resp, resp)
                return
            elif req.path == oauth_flow.redirect_uri_path:
                bolt_resp = oauth_flow.handle_callback(self._to_bolt_request(req))
                self._write_response(bolt_resp, resp)
                return

        resp.status = "404"
        resp.body = "The page is not found..."

    def on_post(self, req: Request, resp: Response):
        bolt_req = self._to_bolt_request(req)
        bolt_resp = self.app.dispatch(bolt_req)
        self._write_response(bolt_resp, resp)

    def _to_bolt_request(self, req: Request) -> BoltRequest:
        return BoltRequest(
            body=req.stream.read(req.content_length or 0).decode("utf-8"),
            query=req.query_string,
            headers={k.lower(): v for k, v in req.headers.items()},
        )

    def _write_response(self, bolt_resp: BoltResponse, resp: Response):
        if falcon_version.__version__.startswith("2."):
            resp.body = bolt_resp.body
        else:
            resp.text = bolt_resp.body

        status = HTTPStatus(bolt_resp.status)
        resp.status = str(f"{status.value} {status.phrase}")
        resp.set_headers(bolt_resp.first_headers_without_set_cookie())
        for cookie in bolt_resp.cookies():
            for name, c in cookie.items():
                expire_value = c.get("expires")
                expire = datetime.strptime(expire_value, "%a, %d %b %Y %H:%M:%S %Z") if expire_value else None
                resp.set_cookie(
                    name=name,
                    value=c.value,
                    expires=expire,
                    max_age=c.get("max-age"),
                    domain=c.get("domain"),
                    path=c.get("path"),
                    secure=True,
                    http_only=True,
                )
