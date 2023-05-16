import logging
from typing import Optional

from aiohttp import web

from slack_bolt.adapter.aiohttp import to_bolt_request, to_aiohttp_response
from slack_bolt.response import BoltResponse
from slack_bolt.util.utils import get_boot_message


class AsyncSlackAppServer:
    port: int
    path: str
    host: str
    bolt_app: "AsyncApp"  # type:ignore
    web_app: web.Application

    def __init__(  # type:ignore
        self,
        port: int,
        path: str,
        app: "AsyncApp",  # type:ignore
        host: Optional[str] = None,
    ):
        """Standalone AIOHTTP Web Server.
        Refer to https://docs.aiohttp.org/en/stable/web.html for details of AIOHTTP.

        Args:
            port: The port to listen on
            path: The path to receive incoming requests from Slack
            app: The `AsyncApp` instance that is used for processing requests
            host: The hostname to serve the web endpoints. (Default: 0.0.0.0)
        """
        self.port = port
        self.path = path
        self.host = host if host is not None else "0.0.0.0"
        self.bolt_app: "AsyncApp" = app  # type: ignore
        self.web_app = web.Application()
        self._bolt_oauth_flow = self.bolt_app.oauth_flow
        if self._bolt_oauth_flow:
            self.web_app.add_routes(
                [
                    web.get(self._bolt_oauth_flow.install_path, self.handle_get_requests),
                    web.get(
                        self._bolt_oauth_flow.redirect_uri_path,
                        self.handle_get_requests,
                    ),
                    web.post(self.path, self.handle_post_requests),
                ]
            )
        else:
            self.web_app.add_routes([web.post(self.path, self.handle_post_requests)])

    async def handle_get_requests(self, request: web.Request) -> web.Response:
        oauth_flow = self._bolt_oauth_flow
        if oauth_flow:
            if request.path == oauth_flow.install_path:
                bolt_req = await to_bolt_request(request)
                bolt_resp = await oauth_flow.handle_installation(bolt_req)
                return await to_aiohttp_response(bolt_resp)
            elif request.path == oauth_flow.redirect_uri_path:
                bolt_req = await to_bolt_request(request)
                bolt_resp = await oauth_flow.handle_callback(bolt_req)
                return await to_aiohttp_response(bolt_resp)
            else:
                return web.Response(status=404)
        else:
            return web.Response(status=404)

    async def handle_post_requests(self, request: web.Request) -> web.Response:
        if self.path != request.path:
            return web.Response(status=404)

        bolt_req = await to_bolt_request(request)
        bolt_resp: BoltResponse = await self.bolt_app.async_dispatch(bolt_req)
        return await to_aiohttp_response(bolt_resp)

    def start(self, host: Optional[str] = None) -> None:
        """Starts a new web server process."""
        if self.bolt_app.logger.level > logging.INFO:
            print(get_boot_message())
        else:
            self.bolt_app.logger.info(get_boot_message())

        _host = host if host is not None else self.host
        web.run_app(self.web_app, host=_host, port=self.port)
