from slack_bolt import App
from slack_bolt.adapter.starlette import SlackRequestHandler

app = App()


@app.event("app_mention")
def handle_app_mentions(body, say, logger):
    logger.info(body)
    say("What's up?")


app_handler = SlackRequestHandler(app)

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route


async def endpoint(req: Request):
    return await app_handler.handle(req)


api = Starlette(debug=True, routes=[Route("/slack/events", endpoint=endpoint, methods=["POST"])])

# pip install -r requirements.txt
# export SLACK_SIGNING_SECRET=***
# export SLACK_BOT_TOKEN=xoxb-***
# uvicorn app:api --reload --port 3000 --log-level debug
