from datetime import datetime  # type: ignore
from http import HTTPStatus

from falcon import version as falcon_version
from falcon.asgi import Request, Response
from slack_bolt import BoltResponse
from slack_bolt.async_app import AsyncApp
from slack_bolt.error import BoltError
from slack_bolt.oauth.async_oauth_flow import AsyncOAuthFlow
from slack_bolt.request.async_request import AsyncBoltRequest


class AsyncSlackAppResource:
    """
    For use with ASGI Falcon Apps.

    from slack_bolt.async_app import AsyncApp
    app = AsyncApp()

    import falcon
    app = falcon.asgi.App()
    app.add_route("/slack/events", AsyncSlackAppResource(app))
    """

    def __init__(self, app: AsyncApp):  # type: ignore
        if falcon_version.__version__.startswith("2."):
            raise BoltError("This ASGI compatible adapter requires Falcon version >= 3.0")

        self.app = app

    async def on_get(self, req: Request, resp: Response):
        if self.app.oauth_flow is not None:
            oauth_flow: AsyncOAuthFlow = self.app.oauth_flow
            if req.path == oauth_flow.install_path:
                bolt_resp = await oauth_flow.handle_installation(await self._to_bolt_request(req))
                await self._write_response(bolt_resp, resp)
                return
            elif req.path == oauth_flow.redirect_uri_path:
                bolt_resp = await oauth_flow.handle_callback(await self._to_bolt_request(req))
                await self._write_response(bolt_resp, resp)
                return

        resp.status = "404"
        resp.body = "The page is not found..."

    async def on_post(self, req: Request, resp: Response):
        bolt_req = await self._to_bolt_request(req)
        bolt_resp = await self.app.async_dispatch(bolt_req)
        await self._write_response(bolt_resp, resp)

    async def _to_bolt_request(self, req: Request) -> AsyncBoltRequest:
        return AsyncBoltRequest(
            body=(await req.stream.read(req.content_length or 0)).decode("utf-8"),
            query=req.query_string,
            headers={k.lower(): v for k, v in req.headers.items()},
        )

    async def _write_response(self, bolt_resp: BoltResponse, resp: Response):
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
