from logging import Logger
from typing import Optional

from slack_sdk.web.async_client import AsyncWebClient

from slack_bolt.version import __version__ as bolt_version


def create_async_web_client(token: Optional[str] = None, logger: Optional[Logger] = None) -> AsyncWebClient:
    return AsyncWebClient(
        token=token,
        logger=logger,
        user_agent_prefix=f"Bolt-Async/{bolt_version}",
    )
