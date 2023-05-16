"""Listeners process an incoming request from Slack if the request's type or data structure matches
the predefined conditions of the listener. Typically, a listener acknowledge requests from Slack,
process the request data, and may send response back to Slack.
"""

# Don't add async module imports here
from .custom_listener import CustomListener
from .listener import Listener

builtin_listener_classes = [
    CustomListener,
]
for cls in builtin_listener_classes:
    Listener.register(cls)

__all__ = [
    "CustomListener",
    "Listener",
    "builtin_listener_classes",
]
