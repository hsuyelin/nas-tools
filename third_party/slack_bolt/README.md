# Bolt ![Bolt logo](docs/assets/bolt-logo.svg) for Python

[![Python Version][python-version]][pypi-url]
[![pypi package][pypi-image]][pypi-url]
[![Build Status][build-image]][build-url]
[![Codecov][codecov-image]][codecov-url]

A Python framework to build Slack apps in a flash with the latest platform features. Read the [getting started guide](https://slack.dev/bolt-python/tutorial/getting-started) and look at our [code examples](https://github.com/slackapi/bolt-python/tree/main/examples) to learn how to build apps using Bolt. The Python module documents are available [here](https://slack.dev/bolt-python/api-docs/slack_bolt/).

## Setup

```bash
# Python 3.6+ required
python -m venv .venv
source .venv/bin/activate

pip install -U pip
pip install slack_bolt
```

## Creating an app

Create a Bolt for Python app by calling a constructor, which is a top-level export. If you'd prefer, you can create an [async app](#creating-an-async-app).

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from slack_bolt import App

# export SLACK_SIGNING_SECRET=***
# export SLACK_BOT_TOKEN=xoxb-***
app = App()

# Add functionality here

if __name__ == "__main__":
    app.start(3000)  # POST http://localhost:3000/slack/events
```

## Running an app

```bash
export SLACK_SIGNING_SECRET=***
export SLACK_BOT_TOKEN=xoxb-***
python app.py

# in another terminal
ngrok http 3000
```

## Running a Socket Mode app

If you use [Socket Mode](https://api.slack.com/socket-mode) for running your app, `SocketModeHandler` is available for it.

```python
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Install the Slack app and get xoxb- token in advance
app = App(token=os.environ["SLACK_BOT_TOKEN"])

# Add functionality here

if __name__ == "__main__":
    # Create an app-level token with connections:write scope
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
```

Run the app this way:

```bash
export SLACK_APP_TOKEN=xapp-***
export SLACK_BOT_TOKEN=xoxb-***
python app.py

# SLACK_SIGNING_SECRET is not required
# Running ngrok is not required
```

## Listening for events

Apps typically react to a collection of incoming events, which can correspond to [Events API events](https://api.slack.com/events-api), [actions](https://api.slack.com/interactivity/components), [shortcuts](https://api.slack.com/interactivity/shortcuts), [slash commands](https://api.slack.com/interactivity/slash-commands) or [options requests](https://api.slack.com/reference/block-kit/block-elements#external_select). For each type of
request, there's a method to build a listener function.

```python
# Listen for an event from the Events API
app.event(event_type)(fn)

# Convenience method to listen to only `message` events using a string or re.Pattern
app.message([pattern ,])(fn)

# Listen for an action from a Block Kit element (buttons, select menus, date pickers, etc)
app.action(action_id)(fn)

# Listen for dialog submissions
app.action({"callback_id": callbackId})(fn)

# Listen for a global or message shortcuts
app.shortcut(callback_id)(fn)

# Listen for slash commands
app.command(command_name)(fn)

# Listen for view_submission modal events
app.view(callback_id)(fn)

# Listen for options requests (from select menus with an external data source)
app.options(action_id)(fn)
```

The recommended way to use these methods are decorators:

```python
@app.event(event_type)
def handle_event(event):
    pass
```

## Making things happen

Most of the app's functionality will be inside listener functions (the `fn` parameters above). These functions are called with a set of arguments, each of which can be used in any order. If you'd like to access arguments off of a single object, you can use `args`, an [`slack_bolt.kwargs_injection.Args`](https://github.com/slackapi/bolt-python/blob/main/slack_bolt/kwargs_injection/args.py) instance that contains all available arguments for that event.

| Argument  | Description  |
| :---: | :--- |
| `body` | Dictionary that contains the entire body of the request (superset of `payload`). Some accessory data is only available outside of the payload (such as `trigger_id` and `authorizations`).
| `payload` | Contents of the incoming event. The payload structure depends on the listener. For example, for an Events API event, `payload` will be the [event type structure](https://api.slack.com/events-api#event_type_structure). For a block action, it will be the action from within the `actions` list. The `payload` dictionary is also accessible via the alias corresponding to the listener (`message`, `event`, `action`, `shortcut`, `view`, `command`, or `options`). For example, if you were building a `message()` listener, you could use the `payload` and `message` arguments interchangably. **An easy way to understand what's in a payload is to log it**. |
| `context` | Event context. This dictionary contains data about the event and app, such as the `botId`. Middleware can add additional context before the event is passed to listeners.
| `ack` | Function that **must** be called to acknowledge that your app received the incoming event. `ack` exists for all actions, shortcuts, view submissions, slash command and options requests. `ack` returns a promise that resolves when complete. Read more in [Acknowledging events](https://slack.dev/bolt-python/concepts#acknowledge).
| `respond` | Utility function that responds to incoming events **if** it contains a `response_url` (shortcuts, actions, and slash commands).
| `say` | Utility function to send a message to the channel associated with the incoming event. This argument is only available when the listener is triggered for events that contain a `channel_id` (the most common being `message` events). `say` accepts simple strings (for plain-text messages) and dictionaries (for messages containing blocks).
| `client` | Web API client that uses the token associated with the event. For single-workspace installations, the token is provided to the constructor. For multi-workspace installations, the token is returned by using [the OAuth library](https://slack.dev/bolt-python/concepts#authenticating-oauth), or manually using the `authorize` function.
| `logger` | The built-in [`logging.Logger`](https://docs.python.org/3/library/logging.html) instance you can use in middleware/listeners.

## Creating an async app

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
Apps can be run the same way as the syncronous example above. If you'd prefer another async Web framework (e.g., Sanic, FastAPI, Starlette), take a look at [the built-in adapters](https://github.com/slackapi/bolt-python/tree/main/slack_bolt/adapter) and their corresponding [examples](https://github.com/slackapi/bolt-python/tree/main/examples).

## Getting Help

[The documentation](https://slack.dev/bolt-python) has more information on basic and advanced concepts for Bolt for Python. Also, all the Python module documents of this library are available [here](https://slack.dev/bolt-python/api-docs/slack_bolt/).

If you otherwise get stuck, we're here to help. The following are the best ways to get assistance working through your issue:

  * [Issue Tracker](http://github.com/slackapi/bolt-python/issues) for questions, bug reports, feature requests, and general discussion related to Bolt for Python. Try searching for an existing issue before creating a new one.
  * [Email](mailto:support@slack.com) our developer support team: `support@slack.com`


[pypi-image]: https://badge.fury.io/py/slack-bolt.svg
[pypi-url]: https://pypi.org/project/slack-bolt/
[build-image]: https://github.com/slackapi/bolt-python/workflows/CI%20Build/badge.svg
[build-url]: https://github.com/slackapi/bolt-python/actions?query=workflow%3A%22CI+Build%22
[codecov-image]: https://codecov.io/gh/slackapi/bolt-python/branch/main/graph/badge.svg
[codecov-url]: https://codecov.io/gh/slackapi/bolt-python
[python-version]: https://img.shields.io/pypi/pyversions/slack-bolt.svg
