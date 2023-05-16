---
title: Using async (asyncio)
lang: en
slug: async
order: 2
---

<div class="section-content">
To use the async version of Bolt, you can import and initialize an `AsyncApp` instance (rather than `App`). `AsyncApp` relies on <a href="https://docs.aiohttp.org/">AIOHTTP</a> to make API requests, which means you'll need to install `aiohttp` (by adding to `requirements.txt` or running `pip install aiohttp`).

Sample async projects can be found within the repository's <a href="https://github.com/slackapi/bolt-python/tree/main/examples">`examples` folder</a>.
</div>

```python
# Requirement: install aiohttp
from slack_bolt.async_app import AsyncApp
app = AsyncApp()

@app.event("app_mention")
async def handle_mentions(event, client, say):  # async function
    api_response = await client.reactions_add(
        channel=event["channel"],
        timestamp=event["ts"],
        name="eyes",
    )
    await say("What's up?")

if __name__ == "__main__":
    app.start(3000)
```

<details class="secondary-wrapper">
<summary class="section-head" markdown="0">
<h4 class="section-head">Using other frameworks</h4>
</summary>

<div class="secondary-content" markdown="0">

Internally `AsyncApp#start()` implements a [`AIOHTTP`](https://docs.aiohttp.org/) web server. If you prefer, you can use a framework other than `AIOHTTP` to handle incoming requests.

This example uses [Sanic](https://sanicframework.org/), but the full list of adapters are in the [`adapter` folder](https://github.com/slackapi/bolt-python/tree/main/slack_bolt/adapter).

The following commands install the necessary requirements and starts the Sanic server on port 3000.

```bash
# Install requirements
pip install slack_bolt sanic uvicorn
# Save the source as async_app.py
uvicorn async_app:api --reload --port 3000 --log-level debug
```
</div>

```python
from slack_bolt.async_app import AsyncApp
app = AsyncApp()

# There is nothing specific to Sanic here!
# AsyncApp is completely framework/runtime agnostic
@app.event("app_mention")
async def handle_app_mentions(say):
    await say("What's up?")

import os
from sanic import Sanic
from sanic.request import Request
from slack_bolt.adapter.sanic import AsyncSlackRequestHandler

# Create an adapter for Sanic with the App instance
app_handler = AsyncSlackRequestHandler(app)
# Create a Sanic app
api = Sanic(name="awesome-slack-app")

@api.post("/slack/events")
async def endpoint(req: Request):
    # app_handler internally runs the App's dispatch method
    return await app_handler.handle(req)

if __name__ == "__main__":
    api.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
```
</details>
