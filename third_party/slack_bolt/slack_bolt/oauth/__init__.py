"""Slack OAuth flow support for building an app that is installable in any workspaces.

Refer to https://slack.dev/bolt-python/concepts#authenticating-oauth for details.
"""

# Don't add async module imports here
from .oauth_flow import OAuthFlow

__all__ = [
    "OAuthFlow",
]
