"""This interface represents Bolt's synchronous response to Slack.

In Socket Mode, the response data can be transformed to a WebSocket message. In the HTTP endpoint mode,
the response data becomes an HTTP response data.

Refer to https://api.slack.com/apis/connections for the two types of connections.
"""

from .response import BoltResponse

__all__ = [
    "BoltResponse",
]
