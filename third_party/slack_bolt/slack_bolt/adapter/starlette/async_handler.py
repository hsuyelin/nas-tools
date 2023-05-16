from typing import Dict, Any, Optional

from starlette.requests import Request
from starlette.responses import Response

from slack_bolt import BoltResponse
from slack_bolt.async_app import AsyncApp, AsyncBoltRequest
from slack_bolt.oauth.async_oauth_flow import AsyncOAuthFlow


def to_async_bolt_request(
    req: Request,
    body: bytes,
    addition_context_properties: Optional[Dict[str, Any]] = None,
) -> AsyncBoltRequest:
    request = AsyncBoltRequest(
        body=body.decode("utf-8"),
        query=req.query_params,
        headers=req.headers,
    )
    if addition_context_properties is not None:
        for k, v in addition_context_properties.items():
            request.context[k] = v
    return request


def to_starlette_response(bolt_resp: BoltResponse) -> Response:
    resp = Response(
        status_code=bolt_resp.status,
        content=bolt_resp.body,
        headers=bolt_resp.first_headers_without_set_cookie(),
    )
    for cookie in bolt_resp.cookies():
        for name, c in cookie.items():
            resp.set_cookie(
                key=name,
                value=c.value,
                max_age=c.get("max-age"),
                expires=c.get("expires"),
                path=c.get("path"),
                domain=c.get("domain"),
                secure=True,
                httponly=True,
            )
    return resp


class AsyncSlackRequestHandler:
    def __init__(self, app: AsyncApp):  # type: ignore
        self.app = app

    async def handle(self, req: Request, addition_context_properties: Optional[Dict[str, Any]] = None) -> Response:
        body = await req.body()
        if req.method == "GET":
            if self.app.oauth_flow is not None:
                oauth_flow: AsyncOAuthFlow = self.app.oauth_flow
                if req.url.path == oauth_flow.install_path:
                    bolt_resp = await oauth_flow.handle_installation(
                        to_async_bolt_request(req, body, addition_context_properties)
                    )
                    return to_starlette_response(bolt_resp)
                elif req.url.path == oauth_flow.redirect_uri_path:
                    bolt_resp = await oauth_flow.handle_callback(
                        to_async_bolt_request(req, body, addition_context_properties)
                    )
                    return to_starlette_response(bolt_resp)
        elif req.method == "POST":
            bolt_resp = await self.app.async_dispatch(to_async_bolt_request(req, body, addition_context_properties))
            return to_starlette_response(bolt_resp)

        return Response(
            status_code=404,
            content="Not found",
        )
