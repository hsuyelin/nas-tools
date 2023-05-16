---
title: Getting started
order: 0
slug: getting-started
lang: en
layout: tutorial
permalink: /tutorial/getting-started
redirect_from:
  - /getting-started
---
# Getting started with Bolt for Python

<div class="section-content">
This guide is meant to walk you through getting up and running with a Slack app using Bolt for Python. Along the way, we’ll create a new Slack app, set up your local environment, and develop an app that listens and responds to messages from a Slack workspace.
</div>

When you're finished, you'll have this ⚡️[Getting Started with Slack app](https://github.com/slackapi/bolt-python/tree/main/examples/getting_started) to run, modify, and make your own.

> 💡 For this guide, we are going to be using [Socket Mode](https://api.slack.com/apis/connections/socket), our recommended option for those just getting started and building something for their team. If you already know you're going to want to use HTTP as your app's communication protocol, head over to our parallel guide, [Getting Started over HTTP](/bolt-python/tutorial/getting-started-http). 
 
---

### Create an app {#create-an-app}
First thing's first: before you start developing with Bolt, you'll want to [create a Slack app](https://api.slack.com/apps/new).

> 💡 We recommend using a workspace where you won't disrupt real work getting done — [you can create a new one for free](https://slack.com/get-started#create).

After you fill out an app name (_you can change it later_) and pick a workspace to install it to, hit the `Create App` button and you'll land on your app's **Basic Information** page.

This page contains an overview of your app in addition to important credentials you'll want to reference later. 

![Basic Information page](../assets/basic-information-page.png "Basic Information page")

Look around, add an app icon and description, and then let's start configuring your app 🔩

---

### Tokens and installing apps {#tokens-and-installing-apps}
Slack apps use [OAuth to manage access to Slack's APIs](https://api.slack.com/docs/oauth). When an app is installed, you'll receive a token that the app can use to call API methods.

There are three main token types available to a Slack app: user (`xoxp`), bot (`xoxb`), and app-level (`xapp`) tokens. 
- [User tokens](https://api.slack.com/authentication/token-types#user) allow you to call API methods on behalf of users after they install or authenticate the app. There may be several user tokens for a single workspace. 
- [Bot tokens](https://api.slack.com/authentication/token-types#bot) are associated with bot users, and are only granted once in a workspace where someone installs the app. The bot token your app uses will be the same no matter which user performed the installation. Bot tokens are the token type that _most_ apps use.
- [App-level tokens](https://api.slack.com/authentication/token-types#app) represent your app across organizations, including installations by all individual users on all workspaces in a given organization and are commonly used for creating WebSocket connections to your app.

We're going to use bot and app-level tokens for this guide.

1. Navigate to the **OAuth & Permissions** on the left sidebar and scroll down to the **Bot Token Scopes** section. Click **Add an OAuth Scope**.

2. For now, we'll just add one scope: [`chat:write`](https://api.slack.com/scopes/chat:write). This grants your app the permission to post messages in channels it's a member of.

3. Scroll up to the top of the **OAuth & Permissions** page and click **Install App to Workspace**. You'll be led through Slack's OAuth UI, where you should allow your app to be installed to your development workspace.

4. Once you authorize the installation, you'll land on the **OAuth & Permissions** page and see a **Bot User OAuth Access Token**. 

![OAuth Tokens](../assets/bot-token.png "Bot OAuth Token")

5. Then head over to **Basic Information** and scroll down under the App Token section and click **Generate Token and Scopes** to generate an app-level token. Add the `connections:write` scope to this token and save the generated `xapp` token, we'll use both these tokens in just a moment. 

6. Navigate to **Socket Mode** on the left side menu and toggle to enable. 


> 💡 Treat your tokens like passwords and [keep them safe](https://api.slack.com/docs/oauth-safety). Your app uses tokens to post and retrieve information from Slack workspaces.

---

### Setting up your project {#setting-up-your-project}
With the initial configuration handled, it's time to set up a new Bolt project. This is where you'll write the code that handles the logic for your app.

If you don’t already have a project, let’s create a new one. Create an empty directory:

```shell
mkdir first-bolt-app
cd first-bolt-app
```

Next, we recommend using a [Python virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment) to manage your project's dependencies. This is a great way to prevent conflicts with your system's Python packages. Let's create and activate a new virtual environment with [Python 3.6 or later](https://www.python.org/downloads/):

```shell
python3 -m venv .venv
source .venv/bin/activate
```

We can confirm that the virtual environment is active by checking that the path to `python3` is _inside_ your project ([a similar command is available on Windows](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#activating-a-virtual-environment)):

```shell
which python3
# Output: /path/to/first-bolt-app/.venv/bin/python3
```

Before we install the Bolt for Python package to your new project, let's save the **bot token** and **app-level token** that were generated when you configured your app. 

1. **Copy your bot (xoxb) token from the OAuth & Permissions page** and store it in a new environment variable. The following example works on Linux and macOS; but [similar commands are available on Windows](https://superuser.com/questions/212150/how-to-set-env-variable-in-windows-cmd-line/212153#212153).
```shell
export SLACK_BOT_TOKEN=xoxb-<your-bot-token>
```

2. **Copy your app-level (xapp) token from the Basic Information page** and then store it in a new environment variable. 
```shell
export SLACK_APP_TOKEN=<your-app-level-token>
```

> 🔒 Remember to keep all tokens secure. At a minimum, you should avoid checking them into public version control, and access them via environment variables as we've done above. Checkout the API documentation for more on [best practices for app security](https://api.slack.com/authentication/best-practices).

Now, let's create your app. Install the `slack_bolt` Python package to your virtual environment using the following command:

```shell
pip install slack_bolt
```

Create a new file called `app.py` in this directory and add the following code:

```python
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
```

Your tokens are enough to create your first Bolt app. Save your `app.py` file then on the command line run the following:

```script
python3 app.py
```

Your app should let you know that it's up and running. 🎉

---

### Setting up events {#setting-up-events}
Your app behaves similarly to people on your team — it can post messages, add emoji reactions, and listen and respond to events. 

To listen for events happening in a Slack workspace (like when a message is posted or when a reaction is posted to a message) you'll use the [Events API to subscribe to event types](https://api.slack.com/events-api).

> 💡 Earlier in this tutorial we enabled Socket Mode. Socket Mode lets apps use the Events API and interactive components without exposing a public HTTP endpoint. This can be helpful during development, or if you're receiving requests from behind a firewall. HTTP is more useful for apps being deployed to hosting environments, or apps intended for distribution via the Slack App Directory. To follow this getting started guide with HTTP instead, head over [here](/bolt-python/tutorial/getting-started-http).  

It's time to tell Slack what events we'd like to listen for.

When an event occurs, Slack will send your app some information about the event, like the user that triggered it and the channel it occurred in. Your app will process the details and can respond accordingly.

Navigate to **Event Subscriptions** on the left sidebar and toggle to enable. Under **Subscribe to Bot Events**, you can add events for your bot to respond to. There are four events related to messages:
- [`message.channels`](https://api.slack.com/events/message.channels) listens for messages in public channels that your app is added to
- [`message.groups`](https://api.slack.com/events/message.groups) listens for messages in 🔒 private channels that your app is added to
- [`message.im`](https://api.slack.com/events/message.im) listens for messages in your app's DMs with users
- [`message.mpim`](https://api.slack.com/events/message.mpim) listens for messages in multi-person DMs that your app is added to

If you want your bot to listen to messages from everywhere it is added to, choose all four message events. After you’ve selected the events you want your bot to listen to, click the green **Save Changes** button.

---

### Listening and responding to a message {#listening-and-responding-to-a-message}
Your app is now ready for some logic. Let's start by using the `message()` method to attach a listener for messages.

The following example listens and responds to all messages in channels/DMs where your app has been added that contain the word "hello":

```python
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Listens to incoming messages that contain "hello"
# To learn available listener arguments,
# visit https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html
@app.message("hello")
def message_hello(message, say):
    # say() sends a message to the channel where the event was triggered
    say(f"Hey there <@{message['user']}>!")

# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
```

If you restart your app, so long as your bot user has been added to the channel/DM, when you send any message that contains "hello", it will respond.

This is a basic example, but it gives you a place to start customizing your app based on your own goals. Let's try something a little more interactive by sending a button rather than plain text.

---

### Sending and responding to actions {#sending-and-responding-to-actions}

To use features like buttons, select menus, datepickers, modals, and shortcuts, you’ll need to enable interactivity. Head over to **Interactivity & Shortcuts** in your app configuration.

> 💡 You’ll notice that with Socket Mode on, basic interactivity is enabled for us by default, so no further action here is needed. If you’re using HTTP, you’ll need to supply a Request URL for Slack to send events to.

When interactivity is enabled, interactions with shortcuts, modals, or interactive components (such as buttons, select menus, and datepickers) will be sent to your app as events.

Now, let's go back to your app's code and add logic to handle those events:
- First, we'll send a message that contains an interactive component (in this case a button)
- Next, we'll listen for the action of a user clicking the button before responding

Below, the code from the last section is modified to send a message containing a button rather than just a string:

```python
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Initializes your app with your bot token and socket mode handler
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    # signing_secret=os.environ.get("SLACK_SIGNING_SECRET") # not required for socket mode
)

# Listens to incoming messages that contain "hello"
@app.message("hello")
def message_hello(message, say):
    # say() sends a message to the channel where the event was triggered
    say(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"Hey there <@{message['user']}>!"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Click Me"},
                    "action_id": "button_click"
                }
            }
        ],
        text=f"Hey there <@{message['user']}>!"
    )

# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()

```

The value inside of `say()` is now an object that contains an array of `blocks`. Blocks are the building components of a Slack message and can range from text to images to datepickers. In this case, your app will respond with a section block that includes a button as an accessory. Since we're using `blocks`, the `text` is a fallback for notifications and accessibility.

You'll notice in the button `accessory` object, there is an `action_id`. This will act as a unique identifier for the button so your app can specify what action it wants to respond to.

> 💡 The [Block Kit Builder](https://app.slack.com/block-kit-builder) is an simple way to prototype your interactive messages. The builder lets you (or anyone on your team) mockup messages and generates the corresponding JSON that you can paste directly in your app.

Now, if you restart your app and say "hello" in a channel your app is in, you'll see a message with a button. But if you click the button, nothing happens (*yet!*).

Let's add a handler to send a followup message when someone clicks the button:

```python
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Listens to incoming messages that contain "hello"
@app.message("hello")
def message_hello(message, say):
    # say() sends a message to the channel where the event was triggered
    say(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"Hey there <@{message['user']}>!"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Click Me"},
                    "action_id": "button_click"
                }
            }
        ],
        text=f"Hey there <@{message['user']}>!"
    )

@app.action("button_click")
def action_button_click(body, ack, say):
    # Acknowledge the action
    ack()
    say(f"<@{body['user']['id']}> clicked the button")

# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
```

You can see that we used `app.action()` to listen for the `action_id` that we named `button_click`. If you restart your app and click the button, you'll see a new message from your app that says you clicked the button.

---

### Next steps {#next-steps}
You just built your first [Bolt for Python app](https://github.com/slackapi/bolt-python/tree/main/examples/getting_started) with Socket Mode! 🎉

Now that you have a basic app up and running, you can start exploring how to make your Bolt app stand out. Here are some ideas about what to explore next:

* Read through the [Basic concepts](/bolt-python/concepts#basic) to learn about the different methods and features your Bolt app has access to.

* Explore the different events your bot can listen to with the [`events()` method](/bolt-python/concepts#event-listening). All of the events are listed [on the API site](https://api.slack.com/events).

* Bolt allows you to [call Web API methods](/bolt-python/concepts#web-api) with the client attached to your app. There are [over 220 methods](https://api.slack.com/methods) on our API site.

* Learn more about the different token types [on our API site](https://api.slack.com/docs/token-types). Your app may need different tokens depending on the actions you want it to perform. For apps that do not use Socket Mode, typically only the bot (`xoxb`) token and Signing Secret are required. For example of this, see our parallel guide [Getting Started with HTTP](/bolt-python/tutorial/getting-started-http). 
