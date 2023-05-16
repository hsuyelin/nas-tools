import logging

from slack_bolt import App

logging.basicConfig(level=logging.DEBUG)
app = App()


@app.command("/hello-bolt-python-heroku")
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


# heroku login
# heroku create
# git remote add heroku https://git.heroku.com/xxx.git

# export SLACK_BOT_TOKEN=xxx
# export SLACK_SIGNING_SECRET=xxx
# heroku config:set SLACK_BOT_TOKEN=$SLACK_BOT_TOKEN
# heroku config:set SLACK_SIGNING_SECRET=$SLACK_SIGNING_SECRET
# git checkout -b main
# git add .
# git commit -m'Initial commit for my awesome Slack app'
# git push heroku main
