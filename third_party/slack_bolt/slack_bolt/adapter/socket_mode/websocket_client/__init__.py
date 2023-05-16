"""[`websocket-client`](https://pypi.org/project/websocket-client/) based implementation"""
import os
from logging import Logger
from time import time
from typing import Optional, Tuple

from slack_sdk import WebClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.websocket_client import SocketModeClient

from slack_bolt import App
from slack_bolt.adapter.socket_mode.base_handler import BaseSocketModeHandler
from slack_bolt.adapter.socket_mode.internals import run_bolt_app, send_response
from slack_bolt.response import BoltResponse


class SocketModeHandler(BaseSocketModeHandler):
    app: App  # type: ignore
    app_token: str
    client: SocketModeClient

    def __init__(  # type: ignore
        self,
        app: App,  # type: ignore
        app_token: Optional[str] = None,
        logger: Optional[Logger] = None,
        web_client: Optional[WebClient] = None,
        ping_interval: float = 10,
        concurrency: int = 10,
        http_proxy_host: Optional[str] = None,
        http_proxy_port: Optional[int] = None,
        http_proxy_auth: Optional[Tuple[str, str]] = None,
        proxy_type: Optional[str] = None,
        trace_enabled: bool = False,
    ):
        """Socket Mode adapter for Bolt apps

        Args:
            app: The Bolt app
            app_token: App-level token starting with `xapp-`
            logger: Custom logger
            web_client: custom `slack_sdk.web.WebClient` instance
            ping_interval: The ping-pong internal (seconds)
            concurrency: The size of the underlying thread pool
            http_proxy_host: HTTP proxy host
            http_proxy_port: HTTP proxy port
            http_proxy_auth: HTTP proxy authentication (username, password)
            proxy_type: Proxy type
            trace_enabled: True if trace-level logging is enabled
        """
        self.app = app
        self.app_token = app_token or os.environ["SLACK_APP_TOKEN"]
        self.client = SocketModeClient(
            app_token=self.app_token,
            logger=logger if logger is not None else app.logger,
            web_client=web_client if web_client is not None else app.client,
            ping_interval=ping_interval,
            concurrency=concurrency,
            http_proxy_host=http_proxy_host,
            http_proxy_port=http_proxy_port,
            http_proxy_auth=http_proxy_auth,
            proxy_type=proxy_type,
            trace_enabled=trace_enabled,
        )
        self.client.socket_mode_request_listeners.append(self.handle)

    def handle(self, client: SocketModeClient, req: SocketModeRequest) -> None:
        start = time()
        bolt_resp: BoltResponse = run_bolt_app(self.app, req)
        send_response(client, req, bolt_resp, start)
