import logging

logging.basicConfig(level=logging.DEBUG)

import os
from slack_bolt import App
from slack_bolt.authorization import AuthorizeResult
from slack_sdk import WebClient


def authorize(enterprise_id, team_id, user_id, client: WebClient, logger):
    logger.info(f"{enterprise_id},{team_id},{user_id}")
    # You can implement your own logic here
    token = os.environ["MY_TOKEN"]
    return AuthorizeResult.from_auth_test_response(
        auth_test_response=client.auth_test(token=token),
        bot_token=token,
    )


app = App(signing_secret=os.environ["SLACK_SIGNING_SECRET"], authorize=authorize)


@app.command("/hello-bolt-python")
def hello_command(ack, body):
    user_id = body["user_id"]
    ack(f"Hi <@{user_id}>!")


@app.event("app_mention")
def event_test(body, say, logger):
    logger.info(body)
    say("What's up?")


if __name__ == "__main__":
    app.start(3000)

# pip install slack_bolt
# export SLACK_SIGNING_SECRET=***
# export MY_TOKEN=xoxb-***
# python app_authorize.py
