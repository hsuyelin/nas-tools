import logging

logging.basicConfig(level=logging.DEBUG)

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.tornado.async_handler import AsyncSlackEventsHandler

app = AsyncApp()


@app.middleware  # or app.use(log_request)
async def log_request(logger, body, next_):
    logger.debug(body)
    await next_()


@app.event("app_mention")
async def event_test(body, say, logger):
    logger.info(body)
    await say("What's up?")


from tornado.web import Application
from tornado.ioloop import IOLoop

api = Application([("/slack/events", AsyncSlackEventsHandler, dict(app=app))])

if __name__ == "__main__":
    api.listen(3000)
    IOLoop.current().start()

# pip install -r requirements.txt
# export SLACK_SIGNING_SECRET=***
# export SLACK_BOT_TOKEN=xoxb-***
# python async_app.py
