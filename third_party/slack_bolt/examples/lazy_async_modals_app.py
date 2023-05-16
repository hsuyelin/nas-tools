import asyncio
import logging
from slack_bolt.async_app import AsyncApp

logging.basicConfig(level=logging.DEBUG)

app = AsyncApp()


@app.middleware  # or app.use(log_request)
async def log_request(logger, body, next):
    logger.debug(body)
    return await next()


async def ack_command(body, ack, logger):
    logger.info(body)
    await ack("Thanks!")


async def post_button_message(respond):
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


async def open_modal(body, client, logger):
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
                },
                {
                    "type": "input",
                    "block_id": "es_b",
                    "element": {
                        "type": "external_select",
                        "action_id": "es_a",
                        "placeholder": {"type": "plain_text", "text": "Select an item"},
                        "min_query_length": 0,
                    },
                    "label": {"type": "plain_text", "text": "Search"},
                },
                {
                    "type": "input",
                    "block_id": "mes_b",
                    "element": {
                        "type": "multi_external_select",
                        "action_id": "mes_a",
                        "placeholder": {"type": "plain_text", "text": "Select an item"},
                        "min_query_length": 0,
                    },
                    "label": {"type": "plain_text", "text": "Search (multi)"},
                },
            ],
        },
    )
    logger.info(res)


app.command("/hello-bolt-python")(
    ack=ack_command,
    lazy=[post_button_message, open_modal],
)


@app.options("es_a")
async def show_options(ack):
    await ack({"options": [{"text": {"type": "plain_text", "text": "Maru"}, "value": "maru"}]})


@app.options("mes_a")
async def show_multi_options(ack):
    await ack(
        {
            "option_groups": [
                {
                    "label": {"type": "plain_text", "text": "Group 1"},
                    "options": [
                        {
                            "text": {"type": "plain_text", "text": "Option 1"},
                            "value": "1-1",
                        },
                        {
                            "text": {"type": "plain_text", "text": "Option 2"},
                            "value": "1-2",
                        },
                    ],
                },
                {
                    "label": {"type": "plain_text", "text": "Group 2"},
                    "options": [
                        {
                            "text": {"type": "plain_text", "text": "Option 1"},
                            "value": "2-1",
                        },
                    ],
                },
            ]
        }
    )


@app.view("view-id")
async def handle_view_submission(ack, body, logger):
    await ack()
    logger.info(body["view"]["state"]["values"])


async def ack_button_click(ack, respond):
    await ack()
    await respond("Loading ...")


async def respond_5_seconds_later(respond):
    await asyncio.sleep(5)
    await respond("Completed!")


app.action("a")(ack=ack_button_click, lazy=[respond_5_seconds_later])

if __name__ == "__main__":
    app.start(3000)

# pip install slack_bolt
# export SLACK_SIGNING_SECRET=***
# export SLACK_BOT_TOKEN=xoxb-***
# python modals_app.py
