import logging

from slack_bolt.async_app import AsyncApp

logging.basicConfig(level=logging.DEBUG)
app = AsyncApp()


@app.command("/hello-bolt-python")
async def hello(body, ack):
    user_id = body["user_id"]
    await ack(f"Hi <@{user_id}>!")


from fastapi import FastAPI, Request

api = FastAPI()

from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler

app_handler = AsyncSlackRequestHandler(app)


@api.post("/slack/events")
async def endpoint(req: Request):
    return await app_handler.handle(req)
