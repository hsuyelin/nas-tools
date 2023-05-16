import logging
import os

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.sanic import AsyncSlackRequestHandler

logging.basicConfig(level=logging.DEBUG)
app = AsyncApp()
app_handler = AsyncSlackRequestHandler(app)


@app.command("/hello-bolt-python")
async def hello(body, ack):
    user_id = body["user_id"]
    await ack(f"Hi <@{user_id}>!")


from sanic import Sanic
from sanic.request import Request

api = Sanic(name="awesome-slack-app")


@api.post("/slack/events")
async def endpoint(req: Request):
    return await app_handler.handle(req)


if __name__ == "__main__":
    api.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
