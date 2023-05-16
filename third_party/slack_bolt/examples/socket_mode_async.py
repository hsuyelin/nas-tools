import logging

logging.basicConfig(level=logging.DEBUG)

import os

from slack_bolt.app.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

# Install the Slack app and get xoxb- token in advance
app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"])


@app.command("/hello-socket-mode")
async def hello_command(ack, body):
    user_id = body["user_id"]
    await ack(f"Hi <@{user_id}>!")


@app.event("app_mention")
async def event_test(event, say):
    await say(f"Hi there, <@{event['user']}>!")


async def ack_shortcut(ack):
    await ack()


async def open_modal(body, client):
    await client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "socket_modal_submission",
            "submit": {
                "type": "plain_text",
                "text": "Submit",
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel",
            },
            "title": {
                "type": "plain_text",
                "text": "Socket Modal",
            },
            "blocks": [
                {
                    "type": "input",
                    "block_id": "q1",
                    "label": {
                        "type": "plain_text",
                        "text": "Write anything here!",
                    },
                    "element": {
                        "action_id": "feedback",
                        "type": "plain_text_input",
                    },
                },
                {
                    "type": "input",
                    "block_id": "q2",
                    "label": {
                        "type": "plain_text",
                        "text": "Can you tell us your favorites?",
                    },
                    "element": {
                        "type": "external_select",
                        "action_id": "favorite-animal",
                        "min_query_length": 0,
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select your favorites",
                        },
                    },
                },
            ],
        },
    )


app.shortcut("socket-mode")(ack=ack_shortcut, lazy=[open_modal])


all_options = [
    {
        "text": {"type": "plain_text", "text": ":cat: Cat"},
        "value": "cat",
    },
    {
        "text": {"type": "plain_text", "text": ":dog: Dog"},
        "value": "dog",
    },
    {
        "text": {"type": "plain_text", "text": ":bear: Bear"},
        "value": "bear",
    },
]


@app.options("favorite-animal")
async def external_data_source_handler(ack, body):
    keyword = body.get("value")
    if keyword is not None and len(keyword) > 0:
        options = [o for o in all_options if keyword in o["text"]["text"]]
        await ack(options=options)
    else:
        await ack(options=all_options)


@app.view("socket_modal_submission")
async def submission(ack):
    await ack()


# export SLACK_APP_TOKEN=xapp-***
# export SLACK_BOT_TOKEN=xoxb-***


async def main():
    handler = AsyncSocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    await handler.start_async()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
