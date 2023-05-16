import logging

logging.basicConfig(level=logging.DEBUG)

import os
from slack_sdk.web.async_client import AsyncWebClient
from slack_bolt.authorization import AuthorizeResult
from slack_bolt.async_app import AsyncApp


async def authorize(enterprise_id, team_id, user_id, client: AsyncWebClient, logger):
    logger.info(f"{enterprise_id},{team_id},{user_id}")
    # You can implement your own logic here
    token = os.environ["MY_TOKEN"]
    return AuthorizeResult.from_auth_test_response(
        auth_test_response=await client.auth_test(token=token),
        bot_token=token,
    )


app = AsyncApp(signing_secret=os.environ["SLACK_SIGNING_SECRET"], authorize=authorize)


@app.event("app_mention")
async def event_test(body, say, logger):
    logger.info(body)
    await say("What's up?")


@app.command("/hello-bolt-python")
# or app.command(re.compile(r"/hello-.+"))(test_command)
async def command(ack, body):
    user_id = body["user_id"]
    await ack(f"Hi <@{user_id}>!")


if __name__ == "__main__":
    app.start(3000)

# pip install slack_bolt
# export SLACK_SIGNING_SECRET=***
# export MY_TOKEN=xoxb-***
# python app.py
