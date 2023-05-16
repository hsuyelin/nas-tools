import logging
import os

from slack_bolt import App

logging.basicConfig(level=logging.DEBUG)
app = App()


@app.command("/hey-google")
def hello(body, ack):
    user_id = body["user_id"]
    ack(f"Hi <@{user_id}>!")


from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


# Only for local debug
if __name__ == "__main__":
    flask_app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
