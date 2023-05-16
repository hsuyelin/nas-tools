from typing import List, Tuple

from pyramid.request import Request
from pyramid.response import Response

from slack_bolt import App, BoltRequest, BoltResponse
from slack_bolt.oauth import OAuthFlow


def to_bolt_request(request: Request) -> BoltRequest:
    body: str = ""
    if request.body is not None:
        if isinstance(request.body, bytes):
            body = request.body.decode("utf-8")
        else:
            body = request.body
    bolt_req = BoltRequest(
        body=body,
        query=request.query_string,
        headers=request.headers,
    )
    return bolt_req


def to_pyramid_response(bolt_resp: BoltResponse) -> Response:
    headers: List[Tuple[str, str]] = []
    for k, vs in bolt_resp.headers.items():
        for v in vs:
            headers.append((k, v))

    return Response(
        status=bolt_resp.status,
        body=bolt_resp.body or "",
        headerlist=headers,
        charset="utf-8",
    )


class SlackRequestHandler:
    def __init__(self, app: App):  # type: ignore
        self.app = app

    def handle(self, request: Request) -> Response:
        if request.method == "GET":
            if self.app.oauth_flow is not None:
                oauth_flow: OAuthFlow = self.app.oauth_flow
                if request.path == oauth_flow.install_path:
                    bolt_req = _attach_pyramid_request_to_context(to_bolt_request(request), request)
                    bolt_resp = oauth_flow.handle_installation(bolt_req)
                    return to_pyramid_response(bolt_resp)
                elif request.path == oauth_flow.redirect_uri_path:
                    bolt_req = _attach_pyramid_request_to_context(to_bolt_request(request), request)
                    bolt_resp = oauth_flow.handle_callback(bolt_req)
                    return to_pyramid_response(bolt_resp)
        elif request.method == "POST":
            bolt_req = _attach_pyramid_request_to_context(to_bolt_request(request), request)
            bolt_resp = self.app.dispatch(bolt_req)
            return to_pyramid_response(bolt_resp)

        return Response(status=404, body="Not found")


def _attach_pyramid_request_to_context(
    bolt_req: BoltRequest,
    request: Request,
) -> BoltRequest:
    # To enable developers to access request-scope attributes such as dbsession,
    # this adapter exposes the underlying pyramid_request object to Bolt listeners
    #
    # Developers can access request props this way:
    # @app.event("app_mention")
    # def handle_app_mention_events(context, logger):
    #     req = context["pyramid_request"]
    #     all = req.dbsession.query(MyModel).all()
    #     logger.info(all)
    #
    bolt_req.context["pyramid_request"] = request
    return bolt_req
