import logging

logging.basicConfig(level=logging.DEBUG)

from slack_bolt import App
from slack_bolt.adapter.bottle import SlackRequestHandler

app = App()


@app.middleware  # or app.use(log_request)
def log_request(logger, body, next):
    logger.debug(body)
    return next()


@app.event("app_mention")
def event_test(ack, body, say, logger):
    logger.info(body)
    say("What's up?")


from bottle import post, request, response, run

handler = SlackRequestHandler(app)


@post("/slack/events")
def slack_events():
    return handler.handle(request, response)


if __name__ == "__main__":
    run(host="0.0.0.0", port=3000, reloader=True)

# pip install -r requirements.txt
# export SLACK_SIGNING_SECRET=***
# export SLACK_BOT_TOKEN=xoxb-***
# python app.py
