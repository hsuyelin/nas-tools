import falcon
import logging
import re
from slack_bolt import App, Respond, Ack
from slack_bolt.adapter.falcon import SlackAppResource
from slack_sdk import WebClient

logging.basicConfig(level=logging.DEBUG)
app = App()


# @app.command("/bolt-py-proto", [lambda body: body["team_id"] == "T03E94MJU"])
def test_command(logger: logging.Logger, body: dict, ack: Ack, respond: Respond):
    logger.info(body)
    ack("thanks!")
    respond(
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
def test_shortcut(ack, client: WebClient, logger, body):
    logger.info(body)
    ack()
    res = client.views_open(
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
def view_submission(ack, body, logger):
    logger.info(body)
    ack()


@app.action("a")
def button_click(logger, action, ack, respond):
    logger.info(action)
    ack()
    respond("Here is my response")


@app.event("app_mention")
def handle_app_mentions(body, say, logger):
    logger.info(body)
    say("What's up?")


api = falcon.API()
resource = SlackAppResource(app)
api.add_route("/slack/events", resource)

# pip install -r requirements.txt
# export SLACK_SIGNING_SECRET=***
# export SLACK_BOT_TOKEN=xoxb-***
# gunicorn app:api --reload -b 0.0.0.0:3000
