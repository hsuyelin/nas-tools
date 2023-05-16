import logging
import os

from slack_bolt import App

logging.basicConfig(level=logging.DEBUG)
bolt_app = App()


@bolt_app.command("/hey-google-app-engine")
def hello(body, ack):
    user_id = body["user_id"]
    ack(f"Hi <@{user_id}>!")


from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler

app = Flask(__name__)
handler = SlackRequestHandler(bolt_app)


@app.route("/_ah/warmup")
def warmup():
    # Handle your warmup logic here, e.g. set up a database connection pool
    return "", 200, {}


@app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


# Only for local debug
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
