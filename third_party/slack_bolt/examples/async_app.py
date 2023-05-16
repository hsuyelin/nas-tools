import logging

logging.basicConfig(level=logging.DEBUG)

from slack_bolt.async_app import AsyncApp

app = AsyncApp()


@app.middleware  # or app.use(log_request)
async def log_request(logger, body, next):
    logger.debug(body)
    return await next()


@app.event("app_mention")
async def event_test(body, say, logger):
    logger.info(body)
    await say("What's up?")


@app.command("/hello-bolt-python")
# or app.command(re.compile(r"/hello-.+"))(test_command)
async def command(ack, body):
    user_id = body["user_id"]
    await ack(f"Hi <@{user_id}>!")


if __name__ == "__main__":
    app.start(3000)

# pip install slack_bolt
# export SLACK_SIGNING_SECRET=***
# export SLACK_BOT_TOKEN=xoxb-***
# python async_app.py
