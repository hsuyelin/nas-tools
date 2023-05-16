"""The base class of asyncio-based Socket Mode client implementation"""
import asyncio
import logging
from typing import Union

from slack_sdk.socket_mode.async_client import AsyncBaseSocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest

from slack_bolt import App
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.util.utils import get_boot_message


class AsyncBaseSocketModeHandler:
    app: Union[App, AsyncApp]  # type: ignore
    client: AsyncBaseSocketModeClient

    async def handle(self, client: AsyncBaseSocketModeClient, req: SocketModeRequest) -> None:
        """Handles Socket Mode envelope requests through a WebSocket connection.

        Args:
            client: this Socket Mode client instance
            req: the request data
        """
        raise NotImplementedError()

    async def connect_async(self):
        """Establishes a new connection with the Socket Mode server"""
        await self.client.connect()

    async def disconnect_async(self):
        """Disconnects the current WebSocket connection with the Socket Mode server"""
        await self.client.disconnect()

    async def close_async(self):
        """Disconnects from the Socket Mode server and cleans the resources this instance holds up"""
        await self.client.close()

    async def start_async(self):
        """Establishes a new connection and then starts infinite sleep
        to prevent the termination of this process.
        If you don't want to have the sleep, use `#connect()` method instead.
        """
        await self.connect_async()
        if self.app.logger.level > logging.INFO:
            print(get_boot_message())
        else:
            self.app.logger.info(get_boot_message())
        await asyncio.sleep(float("inf"))
