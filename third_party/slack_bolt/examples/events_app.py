import re
import logging

logging.basicConfig(level=logging.DEBUG)

from slack_bolt import App

app = App()


@app.middleware  # or app.use(log_request)
def log_request(logger, body, next):
    logger.debug(body)
    return next()


@app.event("app_mention")
def event_test(body, say, logger):
    logger.info(body)
    say("What's up?")


@app.event("reaction_added")
def say_something_to_reaction(say):
    say("OK!")


@app.message("test")
def test_message(logger, body):
    logger.info(body)


@app.message(re.compile("bug"))
def mention_bug(logger, body):
    logger.info(body)


@app.event("message")
def ack_the_rest_of_message_events(logger, body):
    logger.info(body)


if __name__ == "__main__":
    app.start(3000)

# pip install slack_bolt
# export SLACK_SIGNING_SECRET=***
# export SLACK_BOT_TOKEN=xoxb-***
# python events_app.py
