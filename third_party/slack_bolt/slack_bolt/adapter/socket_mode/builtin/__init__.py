"""The built-in implementation, which does not have any external dependencies"""
import os
from logging import Logger
from time import time
from typing import Optional, Dict

from slack_sdk import WebClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.builtin import SocketModeClient

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
        proxy: Optional[str] = None,
        proxy_headers: Optional[Dict[str, str]] = None,
        auto_reconnect_enabled: bool = True,
        trace_enabled: bool = False,
        all_message_trace_enabled: bool = False,
        ping_pong_trace_enabled: bool = False,
        ping_interval: float = 10,
        receive_buffer_size: int = 1024,
        concurrency: int = 10,
    ):
        """Socket Mode adapter for Bolt apps

        Args:
            app: The Bolt app
            app_token: App-level token starting with `xapp-`
            logger: Custom logger
            web_client: custom `slack_sdk.web.WebClient` instance
            proxy: HTTP proxy URL
            proxy_headers: Additional request header for proxy connections
            auto_reconnect_enabled: True if the auto-reconnect logic works
            trace_enabled: True if trace-level logging is enabled
            all_message_trace_enabled: True if trace-logging for all received WebSocket messages is enabled
            ping_pong_trace_enabled: True if trace-logging for all ping-pong communications
            ping_interval: The ping-pong internal (seconds)
            receive_buffer_size: The data length for a single socket recv operation
            concurrency: The size of the underlying thread pool
        """
        self.app = app
        self.app_token = app_token or os.environ["SLACK_APP_TOKEN"]
        self.client = SocketModeClient(
            app_token=self.app_token,
            logger=logger if logger is not None else app.logger,
            web_client=web_client if web_client is not None else app.client,
            proxy=proxy if proxy is not None else app.client.proxy,
            proxy_headers=proxy_headers,
            auto_reconnect_enabled=auto_reconnect_enabled,
            trace_enabled=trace_enabled,
            all_message_trace_enabled=all_message_trace_enabled,
            ping_pong_trace_enabled=ping_pong_trace_enabled,
            ping_interval=ping_interval,
            receive_buffer_size=receive_buffer_size,
            concurrency=concurrency,
        )
        self.client.socket_mode_request_listeners.append(self.handle)

    def handle(self, client: SocketModeClient, req: SocketModeRequest) -> None:
        start = time()
        bolt_resp: BoltResponse = run_bolt_app(self.app, req)
        send_response(client, req, bolt_resp, start)
