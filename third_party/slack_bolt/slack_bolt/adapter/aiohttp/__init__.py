import re

from aiohttp import web

from slack_bolt.request.async_request import AsyncBoltRequest
from slack_bolt.response import BoltResponse


async def to_bolt_request(request: web.Request) -> AsyncBoltRequest:
    return AsyncBoltRequest(
        body=await request.text(),
        query=request.query_string,
        headers=request.headers,
    )


async def to_aiohttp_response(bolt_resp: BoltResponse) -> web.Response:
    content_type = bolt_resp.headers.pop(
        "content-type",
        ["application/json" if bolt_resp.body.startswith("{") else "text/plain"],
    )[0]
    content_type = re.sub(r";\s*charset=utf-8", "", content_type)
    resp = web.Response(
        status=bolt_resp.status,
        body=bolt_resp.body,
        headers=bolt_resp.first_headers_without_set_cookie(),
        content_type=content_type,
    )
    for cookie in bolt_resp.cookies():
        for name, c in cookie.items():
            resp.set_cookie(
                name=name,
                value=c.value,
                max_age=c.get("max-age"),
                expires=c.get("expires"),
                path=c.get("path"),
                domain=c.get("domain"),
                secure=True,
                httponly=True,
            )
    return resp


__all__ = [
    "to_bolt_request",
    "to_aiohttp_response",
]
