"""Module for creating asyncio based apps

### Creating an async app

If you'd prefer to build your app with [asyncio](https://docs.python.org/3/library/asyncio.html), you can import the [AIOHTTP](https://docs.aiohttp.org/en/stable/) library and call the `AsyncApp` constructor. Within async apps, you can use the async/await pattern.

```bash
# Python 3.6+ required
python -m venv .venv
source .venv/bin/activate

pip install -U pip
# aiohttp is required
pip install slack_bolt aiohttp
```

In async apps, all middleware/listeners must be async functions. When calling utility methods (like `ack` and `say`) within these functions, it's required to use the `await` keyword.

```python
# Import the async app instead of the regular one
from slack_bolt.async_app import AsyncApp

app = AsyncApp()

@app.event("app_mention")
async def event_test(body, say, logger):
    logger.info(body)
    await say("What's up?")

@app.command("/hello-bolt-python")
async def command(ack, body, respond):
    await ack()
    await respond(f"Hi <@{body['user_id']}>!")

if __name__ == "__main__":
    app.start(3000)
```

If you want to use another async Web framework (e.g., Sanic, FastAPI, Starlette), take a look at the built-in adapters and their examples.

* [The Bolt app examples](https://github.com/slackapi/bolt-python/tree/main/examples)
* [The built-in adapters](https://github.com/slackapi/bolt-python/tree/main/slack_bolt/adapter)
Apps can be run the same way as the synchronous example above. If you'd prefer another async Web framework (e.g., Sanic, FastAPI, Starlette), take a look at [the built-in adapters](https://github.com/slackapi/bolt-python/tree/main/slack_bolt/adapter) and their corresponding [examples](https://github.com/slackapi/bolt-python/tree/main/examples).

Refer to `slack_bolt.app.async_app` for more details.
"""  # noqa: E501
from .app.async_app import AsyncApp
from .context.ack.async_ack import AsyncAck
from .context.async_context import AsyncBoltContext
from .context.respond.async_respond import AsyncRespond
from .context.say.async_say import AsyncSay
from .listener.async_listener import AsyncListener
from .listener_matcher.async_listener_matcher import AsyncCustomListenerMatcher
from .request.async_request import AsyncBoltRequest

__all__ = [
    "AsyncApp",
    "AsyncAck",
    "AsyncBoltContext",
    "AsyncRespond",
    "AsyncSay",
    "AsyncListener",
    "AsyncCustomListenerMatcher",
    "AsyncBoltRequest",
]
