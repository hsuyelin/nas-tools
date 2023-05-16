import logging
import os

from slack_bolt.async_app import AsyncApp

logging.basicConfig(level=logging.DEBUG)
app = AsyncApp()


@app.command("/hey-google")
async def hello(body, ack):
    user_id = body["user_id"]
    await ack(f"Hi <@{user_id}>!")


if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
