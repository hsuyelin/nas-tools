import logging
from slack_bolt import App
from slack_bolt.adapter.tornado import SlackEventsHandler, SlackOAuthHandler

logging.basicConfig(level=logging.DEBUG)
app = App()


@app.middleware  # or app.use(log_request)
def log_request(logger, body, next):
    logger.debug(body)
    next()


@app.event("app_mention")
def event_test(body, say, logger):
    logger.info(body)
    say("What's up?")


from tornado.web import Application
from tornado.ioloop import IOLoop

api = Application(
    [
        ("/slack/events", SlackEventsHandler, dict(app=app)),
        ("/slack/install", SlackOAuthHandler, dict(app=app)),
        ("/slack/oauth_redirect", SlackOAuthHandler, dict(app=app)),
    ]
)

if __name__ == "__main__":
    api.listen(3000)
    IOLoop.current().start()

# pip install -r requirements.txt

# # -- OAuth flow -- #
# export SLACK_SIGNING_SECRET=***
# export SLACK_BOT_TOKEN=xoxb-***
# export SLACK_CLIENT_ID=111.111
# export SLACK_CLIENT_SECRET=***
# export SLACK_SCOPES=app_mentions:read,chat:write

# python oauth_app.py
