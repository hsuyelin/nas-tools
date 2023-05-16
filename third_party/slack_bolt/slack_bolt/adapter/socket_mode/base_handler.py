"""The base class of Socket Mode client implementation.
If you want to build asyncio-based ones, use `AsyncBaseSocketModeHandler` instead.
"""
import logging
import signal
import sys
from threading import Event

from slack_sdk.socket_mode.client import BaseSocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest

from slack_bolt import App
from slack_bolt.util.utils import get_boot_message


class BaseSocketModeHandler:
    app: App  # type: ignore
    client: BaseSocketModeClient

    def handle(self, client: BaseSocketModeClient, req: SocketModeRequest) -> None:
        """Handles Socket Mode envelope requests through a WebSocket connection.

        Args:
            client: this Socket Mode client instance
            req: the request data
        """
        raise NotImplementedError()

    def connect(self):
        """Establishes a new connection with the Socket Mode server"""
        self.client.connect()

    def disconnect(self):
        """Disconnects the current WebSocket connection with the Socket Mode server"""
        self.client.disconnect()

    def close(self):
        """Disconnects from the Socket Mode server and cleans the resources this instance holds up"""
        self.client.close()

    def start(self):
        """Establishes a new connection and then blocks the current thread
        to prevent the termination of this process.
        If you don't want to block the current thread, use `#connect()` method instead.
        """
        self.connect()
        if self.app.logger.level > logging.INFO:
            print(get_boot_message())
        else:
            self.app.logger.info(get_boot_message())

        if sys.platform == "win32":
            # Ctrl+C etc does not work on Windows OS
            # see https://bugs.python.org/issue35935 for details
            signal.signal(signal.SIGINT, signal.SIG_DFL)

        Event().wait()
