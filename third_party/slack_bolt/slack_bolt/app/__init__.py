# flake8: noqa
"""Application interface in Bolt.

For most use cases, we recommend using `slack_bolt.app.app`.
If you already have knowledge about asyncio and prefer the programming model,
you can use `slack_bolt.app.async_app` for building async apps.\
"""

# Don't add async module imports here
from .app import App  # type: ignore

__all__ = [
    "App",
]
