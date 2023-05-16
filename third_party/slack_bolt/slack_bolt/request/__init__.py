"""Incoming request from Slack through either HTTP request or Socket Mode connection.

Refer to https://api.slack.com/apis/connections for the two types of connections.
This interface encapsulates the difference between the two.
"""
# Don't add async module imports here
from .request import BoltRequest

__all__ = [
    "BoltRequest",
]
