---
title: Using Socket Mode
lang: en
slug: socket-mode
order: 16
---

<div class="section-content">
With the introduction of [Socket Mode](https://api.slack.com/apis/connections/socket), Bolt for Python introduced support in version `1.2.0`. With Socket Mode, instead of creating a server with endpoints that Slack sends payloads too, the app will instead connect to Slack via a WebSocket connection and receive data from Slack over the socket connection. Make sure to enable Socket Mode in your app configuration settings. 

To use the Socket Mode, add `SLACK_APP_TOKEN` as an environment variable. You can get your App Token in your app configuration settings under the **Basic Information** section. 

While we recommend using [the built-in Socket Mode adapter](https://github.com/slackapi/bolt-python/tree/main/slack_bolt/adapter/socket_mode/builtin), there are a few other 3rd party library based implementations. Here is the list of available adapters.

|PyPI Project|Bolt Adapter|
|-|-|
|[slack_sdk](https://pypi.org/project/slack-sdk/)|[slack_bolt.adapter.socket_mode](https://github.com/slackapi/bolt-python/tree/main/slack_bolt/adapter/socket_mode/builtin)|
|[websocket_client](https://pypi.org/project/websocket_client/)|[slack_bolt.adapter.socket_mode.websocket_client](https://github.com/slackapi/bolt-python/tree/main/slack_bolt/adapter/socket_mode/websocket_client)|
|[aiohttp](https://pypi.org/project/aiohttp/) (asyncio-based)|[slack_bolt.adapter.socket_mode.aiohttp](https://github.com/slackapi/bolt-python/tree/main/slack_bolt/adapter/socket_mode/aiohttp)|
|[websockets](https://pypi.org/project/websockets/) (asyncio-based)|[slack_bolt.adapter.socket_mode.websockets](https://github.com/slackapi/bolt-python/tree/main/slack_bolt/adapter/socket_mode/websockets)|

</div>

```python
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Install the Slack app and get xoxb- token in advance
app = App(token=os.environ["SLACK_BOT_TOKEN"])

# Add middleware / listeners here

if __name__ == "__main__":
    # export SLACK_APP_TOKEN=xapp-***
    # export SLACK_BOT_TOKEN=xoxb-***
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
```

<details class="secondary-wrapper">
<summary markdown="0">
<h4 class="secondary-header">Using Async (asyncio)</h4>
</summary>

<div class="secondary-content" markdown="0">
To use the asyncio-based adapters such as aiohttp, your whole app needs to be compatible with asyncio's async/await programming model. `AsyncSocketModeHandler` is available for running `AsyncApp` and its async middleware and listeners. 

To learn how to use `AsyncApp`, checkout the [Using Async](https://slack.dev/bolt-python/concepts#async) document and relevant [examples](https://github.com/slackapi/bolt-python/tree/main/examples).
</div>

```python
from slack_bolt.app.async_app import AsyncApp
# The default is the aiohttp based implementation
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"])

# Add middleware / listeners here

async def main():
    handler = AsyncSocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    await handler.start_async()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

</details>
