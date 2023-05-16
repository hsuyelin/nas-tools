import logging
import re
from typing import Callable

from slack_bolt import App, Say, BoltContext
from slack_sdk import WebClient

logging.basicConfig(level=logging.DEBUG)

app = App()


@app.middleware
def log_request(logger: logging.Logger, body: dict, next: Callable):
    logger.debug(body)
    return next()


@app.message("test")
def reply_to_test(say):
    say("Yes, tests are important!")


@app.message(re.compile("bug"))
def mention_bug(say):
    say("Do you mind filing a ticket?")


# middleware function
def extract_subtype(body: dict, context: BoltContext, next: Callable):
    context["subtype"] = body.get("event", {}).get("subtype", None)
    next()


# https://api.slack.com/events/message
# Newly posted messages only
# or @app.event("message")
@app.event({"type": "message", "subtype": None})
def reply_in_thread(body: dict, say: Say):
    event = body["event"]
    thread_ts = event.get("thread_ts", None) or event["ts"]
    say(text="Hey, what's up?", thread_ts=thread_ts)


@app.event(
    event={"type": "message", "subtype": "message_deleted"},
    matchers=[
        # Skip the deletion of messages by this listener
        lambda body: "You've deleted a message: "
        not in body["event"]["previous_message"]["text"]
    ],
)
def detect_deletion(say: Say, body: dict):
    text = body["event"]["previous_message"]["text"]
    say(f"You've deleted a message: {text}")


# https://api.slack.com/events/message/file_share
# https://api.slack.com/events/message/bot_message
@app.event(
    event={"type": "message", "subtype": re.compile("(me_message)|(file_share)")},
    middleware=[extract_subtype],
)
def add_reaction(body: dict, client: WebClient, context: BoltContext, logger: logging.Logger):
    subtype = context["subtype"]  # by extract_subtype
    logger.info(f"subtype: {subtype}")
    message_ts = body["event"]["ts"]
    api_response = client.reactions_add(
        channel=context.channel_id,
        timestamp=message_ts,
        name="eyes",
    )
    logger.info(f"api_response: {api_response}")


# This listener handles all uncaught message events
# (The position in source code matters)
@app.event({"type": "message"}, middleware=[extract_subtype])
def just_ack(logger, context):
    subtype = context["subtype"]  # by extract_subtype
    logger.info(f"{subtype} is ignored")


if __name__ == "__main__":
    app.start(3000)

# pip install slack_bolt
# export SLACK_SIGNING_SECRET=***
# export SLACK_BOT_TOKEN=xoxb-***
# python message_events.py
