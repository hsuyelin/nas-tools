import os
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.sanic import AsyncSlackRequestHandler

app = AsyncApp()
app_handler = AsyncSlackRequestHandler(app)


@app.event("app_mention")
async def handle_app_mentions(body, say, logger):
    logger.info(body)
    await say("What's up?")


from sanic import Sanic
from sanic.request import Request

api = Sanic(name="awesome-slack-app")


@api.post("/slack/events")
async def endpoint(req: Request):
    return await app_handler.handle(req)


if __name__ == "__main__":
    api.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))


# pip install -r requirements.txt
# export SLACK_SIGNING_SECRET=***
# export SLACK_BOT_TOKEN=xoxb-***
# uvicorn async_app:api --reload --port 3000 --log-level debug
