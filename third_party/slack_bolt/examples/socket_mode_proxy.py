import logging

logging.basicConfig(level=logging.DEBUG)

import os

from slack_sdk import WebClient
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# pip3 install proxy.py
# proxy --port 9000 --log-level d
proxy_url = "http://localhost:9000"

# Install the Slack app and get xoxb- token in advance
app = App(client=WebClient(token=os.environ["SLACK_BOT_TOKEN"], proxy=proxy_url))


@app.event("app_mention")
def event_test(event, say):
    say(f"Hi there, <@{event['user']}>!")


if __name__ == "__main__":
    # export SLACK_APP_TOKEN=xapp-***
    # export SLACK_BOT_TOKEN=xoxb-***
    SocketModeHandler(
        app=app,
        app_token=os.environ["SLACK_APP_TOKEN"],
        proxy=proxy_url,
    ).start()
