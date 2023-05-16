from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.asgi.async_handler import AsyncSlackRequestHandler

app = AsyncApp()


@app.event("app_mention")
async def handle_app_mentions(body, say, logger):
    logger.info(body)
    await say("What's up?")


api = AsyncSlackRequestHandler(app)

# pip install -r requirements.txt
# export SLACK_SIGNING_SECRET=***
# export SLACK_BOT_TOKEN=xoxb-***
# uvicorn async_app:api --reload --port 3000 --log-level debug
# ngrok http 3000
