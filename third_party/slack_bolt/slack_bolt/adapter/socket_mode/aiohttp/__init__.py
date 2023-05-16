"""[`aiohttp`](https://pypi.org/project/aiohttp/) based implementation / asyncio compatible"""
import os
from logging import Logger
from time import time
from typing import Optional

from slack_sdk.socket_mode.aiohttp import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.web.async_client import AsyncWebClient

from slack_bolt import App
from slack_bolt.adapter.socket_mode.async_base_handler import AsyncBaseSocketModeHandler
from slack_bolt.adapter.socket_mode.async_internals import (
    send_async_response,
    run_async_bolt_app,
)
from slack_bolt.adapter.socket_mode.internals import run_bolt_app
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.response import BoltResponse


class SocketModeHandler(AsyncBaseSocketModeHandler):
    app: App  # type: ignore
    app_token: str
    client: SocketModeClient

    def __init__(  # type: ignore
        self,
        app: App,  # type: ignore
        app_token: Optional[str] = None,
        logger: Optional[Logger] = None,
        web_client: Optional[AsyncWebClient] = None,
        proxy: Optional[str] = None,
        ping_interval: float = 10,
    ):
        """Socket Mode adapter for Bolt apps

        Args:
            app: The Bolt app
            app_token: App-level token starting with `xapp-`
            logger: Custom logger
            web_client: custom `slack_sdk.web.WebClient` instance
            proxy: HTTP proxy URL
            ping_interval: The ping-pong internal (seconds)
        """
        self.app = app
        self.app_token = app_token or os.environ["SLACK_APP_TOKEN"]
        self.client = SocketModeClient(
            app_token=self.app_token,
            logger=logger if logger is not None else app.logger,
            web_client=web_client if web_client is not None else app.client,
            proxy=proxy,
            ping_interval=ping_interval,
        )
        self.client.socket_mode_request_listeners.append(self.handle)

    async def handle(self, client: SocketModeClient, req: SocketModeRequest) -> None:
        start = time()
        bolt_resp: BoltResponse = run_bolt_app(self.app, req)
        await send_async_response(client, req, bolt_resp, start)


class AsyncSocketModeHandler(AsyncBaseSocketModeHandler):
    app: AsyncApp  # type: ignore
    app_token: str
    client: SocketModeClient

    def __init__(  # type: ignore
        self,
        app: AsyncApp,  # type: ignore
        app_token: Optional[str] = None,
        logger: Optional[Logger] = None,
        web_client: Optional[AsyncWebClient] = None,
        proxy: Optional[str] = None,
        ping_interval: float = 10,
    ):
        self.app = app
        self.app_token = app_token or os.environ["SLACK_APP_TOKEN"]
        self.client = SocketModeClient(
            app_token=self.app_token,
            logger=logger if logger is not None else app.logger,
            web_client=web_client if web_client is not None else app.client,
            proxy=proxy,
            ping_interval=ping_interval,
        )
        self.client.socket_mode_request_listeners.append(self.handle)

    async def handle(self, client: SocketModeClient, req: SocketModeRequest) -> None:
        start = time()
        bolt_resp: BoltResponse = await run_async_bolt_app(self.app, req)
        await send_async_response(client, req, bolt_resp, start)
