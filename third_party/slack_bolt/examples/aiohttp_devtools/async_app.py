import logging

logging.basicConfig(level=logging.DEBUG)

from slack_bolt.async_app import AsyncApp

app = AsyncApp()


@app.event("app_mention")
async def event_test(body, say, logger):
    logger.info(body)
    await say("What's up?")


@app.command("/hello-bolt-python")
# or app.command(re.compile(r"/hello-.+"))(test_command)
async def command(ack, body):
    user_id = body["user_id"]
    await ack(f"Hi <@{user_id}>!")


def app_factory():
    return app.web_app()


# pip install -r requirements.txt
# export SLACK_SIGNING_SECRET=***
# export SLACK_BOT_TOKEN=xoxb-***
# adev runserver --port 3000 --app-factory app_factory async_app.py
