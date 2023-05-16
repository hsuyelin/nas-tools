"""Socket Mode adapter package provides the following implementations. If you don't have strong reasons to use 3rd party library based adapters, we recommend using the built-in client based one.

* `slack_bolt.adapter.socket_mode.builtin`
* `slack_bolt.adapter.socket_mode.websocket_client`
* `slack_bolt.adapter.socket_mode.aiohttp`
* `slack_bolt.adapter.socket_mode.websockets`
"""  # noqa: E501

# Don't add async module imports here
from .builtin import SocketModeHandler

__all__ = [
    "SocketModeHandler",
]
