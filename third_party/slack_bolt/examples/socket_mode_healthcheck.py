import logging
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

logging.basicConfig(level=logging.DEBUG)

#
# Socket Mode Bolt app
#

# Install the Slack app and get xoxb- token in advance
app = App(token=os.environ["SLACK_BOT_TOKEN"])
socket_mode_handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])


@app.event("app_mention")
def event_test(event, say):
    say(f"Hi there, <@{event['user']}>!")


#
# Web app for hosting the healthcheck endpoint for k8s etc.
#

# pip install Flask
from flask import Flask, make_response

flask_app = Flask(__name__)


@flask_app.route("/health", methods=["GET"])
def slack_events():
    if socket_mode_handler.client is not None and socket_mode_handler.client.is_connected():
        return make_response("OK", 200)
    return make_response("The Socket Mode client is inactive", 503)


#
# Start the app
#
# export SLACK_APP_TOKEN=xapp-***
# export SLACK_BOT_TOKEN=xoxb-***

if __name__ == "__main__":
    socket_mode_handler.connect()  # does not block the current thread
    flask_app.run(port=8080)
