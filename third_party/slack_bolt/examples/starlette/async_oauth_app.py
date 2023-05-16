from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.starlette.async_handler import AsyncSlackRequestHandler

app = AsyncApp()
app_handler = AsyncSlackRequestHandler(app)


@app.event("app_mention")
async def handle_app_mentions(body, say, logger):
    logger.info(body)
    await say("What's up?")


from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route


async def endpoint(req: Request):
    return await app_handler.handle(req)


async def install(req: Request):
    return await app_handler.handle(req)


async def oauth_redirect(req: Request):
    return await app_handler.handle(req)


api = Starlette(
    debug=True,
    routes=[
        Route("/slack/events", endpoint=endpoint, methods=["POST"]),
        Route("/slack/install", endpoint=install, methods=["GET"]),
        Route("/slack/oauth_redirect", endpoint=oauth_redirect, methods=["GET"]),
    ],
)

# pip install -r requirements.txt

# # -- OAuth flow -- #
# export SLACK_SIGNING_SECRET=***
# export SLACK_CLIENT_ID=111.111
# export SLACK_CLIENT_SECRET=***
# export SLACK_SCOPES=app_mentions:read,channels:history,im:history,chat:write

# uvicorn async_oauth_app:api --reload --port 3000 --log-level debug
