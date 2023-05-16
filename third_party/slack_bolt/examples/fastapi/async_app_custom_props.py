import logging

logging.basicConfig(level=logging.DEBUG)

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler

app = AsyncApp()
app_handler = AsyncSlackRequestHandler(app)


@app.event("app_mention")
async def handle_app_mentions(context, say, logger):
    logger.info(context)
    assert context.get("foo") == "FOO"
    await say("What's up?")


@app.event("message")
async def handle_message():
    pass


from fastapi import FastAPI, Request, Depends

api = FastAPI()


def get_foo():
    yield "FOO"


@api.post("/slack/events")
async def endpoint(req: Request, foo: str = Depends(get_foo)):
    return await app_handler.handle(req, {"foo": foo})


# pip install -r requirements.txt
# export SLACK_SIGNING_SECRET=***
# export SLACK_BOT_TOKEN=xoxb-***
# uvicorn async_app_custom_props:api --reload --port 3000 --log-level warning
