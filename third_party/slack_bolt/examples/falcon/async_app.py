import falcon
import logging
import re
from slack_bolt.async_app import AsyncApp, AsyncRespond, AsyncAck
from slack_bolt.adapter.falcon import AsyncSlackAppResource

logging.basicConfig(level=logging.DEBUG)
app = AsyncApp()


# @app.command("/bolt-py-proto", [lambda body: body["team_id"] == "T03E94MJU"])
async def test_command(logger: logging.Logger, body: dict, ack: AsyncAck, respond: AsyncRespond):
    logger.info(body)
    await ack("thanks!")
    await respond(
        blocks=[
            {
                "type": "section",
                "block_id": "b",
                "text": {
                    "type": "mrkdwn",
                    "text": "You can add a button alongside text in your message. ",
                },
                "accessory": {
                    "type": "button",
                    "action_id": "a",
                    "text": {"type": "plain_text", "text": "Button"},
                    "value": "click_me_123",
                },
            }
        ]
    )


app.command(re.compile(r"/hello-bolt-.+"))(test_command)


@app.shortcut("test-shortcut")
async def test_shortcut(ack, client, logger, body):
    logger.info(body)
    await ack()
    res = await client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "view-id",
            "title": {
                "type": "plain_text",
                "text": "My App",
            },
            "submit": {
                "type": "plain_text",
                "text": "Submit",
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel",
            },
            "blocks": [
                {
                    "type": "input",
                    "element": {"type": "plain_text_input"},
                    "label": {
                        "type": "plain_text",
                        "text": "Label",
                    },
                }
            ],
        },
    )
    logger.info(res)


@app.view("view-id")
async def view_submission(ack, body, logger):
    logger.info(body)
    await ack()


@app.action("a")
async def button_click(logger, action, ack, respond):
    logger.info(action)
    await ack()
    await respond("Here is my response")


@app.event("app_mention")
async def handle_app_mentions(body, say, logger):
    logger.info(body)
    await say("What's up?")


api = falcon.asgi.App()
resource = AsyncSlackAppResource(app)
api.add_route("/slack/events", resource)

# pip install -r requirements.txt
# export SLACK_SIGNING_SECRET=***
# export SLACK_BOT_TOKEN=xoxb-***
# uvicorn --reload -h 0.0.0.0 -p 3000 async_app:api
