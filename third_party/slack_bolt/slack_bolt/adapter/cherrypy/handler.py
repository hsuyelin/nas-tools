from typing import Optional

import cherrypy

from slack_bolt.app import App
from slack_bolt.oauth import OAuthFlow
from slack_bolt.request import BoltRequest
from slack_bolt.response import BoltResponse


def build_bolt_request() -> BoltRequest:
    req = cherrypy.request
    body = req.raw_body if hasattr(req, "raw_body") else ""
    return BoltRequest(
        body=body,
        query=req.query_string,
        headers=req.headers,
    )


def set_response_status_and_headers(bolt_resp: BoltResponse) -> None:
    cherrypy.response.status = bolt_resp.status
    for k, v in bolt_resp.first_headers_without_set_cookie().items():
        cherrypy.response.headers[k] = v
    for cookie in bolt_resp.cookies():
        for name, c in cookie.items():
            str_max_age: Optional[str] = c.get("max-age")
            max_age: Optional[int] = int(str_max_age) if str_max_age else None
            cherrypy_cookie = cherrypy.response.cookie
            cherrypy_cookie[name] = c.value
            cherrypy_cookie[name]["expires"] = c.get("expires")
            cherrypy_cookie[name]["max-age"] = max_age
            cherrypy_cookie[name]["domain"] = c.get("domain")
            cherrypy_cookie[name]["path"] = c.get("path")
            cherrypy_cookie[name]["secure"] = True
            cherrypy_cookie[name]["httponly"] = True


@cherrypy.tools.register("on_start_resource")
def slack_in():
    request = cherrypy.serving.request

    def slack_processor(entity):
        try:
            if request.process_request_body:
                body = entity.fp.read()
                body = body.decode("utf-8") if isinstance(body, bytes) else ""
                request.raw_body = body
        except ValueError:
            raise cherrypy.HTTPError(400, "Invalid request body")

    request.body.processors.clear()
    request.body.processors["application/json"] = slack_processor
    request.body.processors["application/x-www-form-urlencoded"] = slack_processor


class SlackRequestHandler:
    def __init__(self, app: App):  # type: ignore
        self.app = app

    def handle(self) -> bytes:
        req = cherrypy.request
        if req.method == "GET":
            if self.app.oauth_flow is not None:
                oauth_flow: OAuthFlow = self.app.oauth_flow
                request_path = req.wsgi_environ["REQUEST_URI"].split("?")[0]
                if request_path == oauth_flow.install_path:
                    bolt_resp = oauth_flow.handle_installation(build_bolt_request())
                    set_response_status_and_headers(bolt_resp)
                    return (bolt_resp.body or "").encode("utf-8")
                elif request_path == oauth_flow.redirect_uri_path:
                    bolt_resp = oauth_flow.handle_callback(build_bolt_request())
                    set_response_status_and_headers(bolt_resp)
                    return (bolt_resp.body or "").encode("utf-8")
        elif req.method == "POST":
            bolt_resp: BoltResponse = self.app.dispatch(build_bolt_request())
            set_response_status_and_headers(bolt_resp)
            return (bolt_resp.body or "").encode("utf-8")

        cherrypy.response.status = 404
        return "Not Found".encode("utf-8")
