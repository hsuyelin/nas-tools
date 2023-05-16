from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.starlette.async_handler import AsyncSlackRequestHandler

app = AsyncApp()


@app.event("app_mention")
async def handle_app_mentions(body, say, logger):
    logger.info(body)
    await say("What's up?")


app_handler = AsyncSlackRequestHandler(app)

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route


async def endpoint(req: Request):
    return await app_handler.handle(req)


api = Starlette(debug=True, routes=[Route("/slack/events", endpoint=endpoint, methods=["POST"])])

# pip install -r requirements.txt
# export SLACK_SIGNING_SECRET=***
# export SLACK_BOT_TOKEN=xoxb-***
# uvicorn async_app:api --reload --port 3000 --log-level debug
