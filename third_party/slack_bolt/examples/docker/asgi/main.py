import logging
from slack_bolt import App
from slack_bolt.adapter.asgi import SlackRequestHandler

logging.basicConfig(level=logging.DEBUG)
app = App()


@app.event("app_mention")
def handle_app_mentions(body, say, logger):
    logger.info(body)
    say("What's up?")


asgi_app = SlackRequestHandler(app)
