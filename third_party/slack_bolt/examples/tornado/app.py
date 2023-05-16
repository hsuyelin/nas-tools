import logging

logging.basicConfig(level=logging.DEBUG)

from slack_bolt import App
from slack_bolt.adapter.tornado import SlackEventsHandler

app = App()


@app.middleware  # or app.use(log_request)
def log_request(logger, body, next_):
    logger.debug(body)
    next_()


@app.event("app_mention")
def event_test(body, say, logger):
    logger.info(body)
    say("What's up?")


from tornado.web import Application
from tornado.ioloop import IOLoop

api = Application([("/slack/events", SlackEventsHandler, dict(app=app))])

if __name__ == "__main__":
    api.listen(3000)
    IOLoop.current().start()

# pip install -r requirements.txt
# export SLACK_SIGNING_SECRET=***
# export SLACK_BOT_TOKEN=xoxb-***
# python app.py
