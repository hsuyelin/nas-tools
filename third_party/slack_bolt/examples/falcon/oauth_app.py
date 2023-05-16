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
    respond("Here is my response.")
    # say(text="say!")


@app.event("app_mention")
def handle_app_mentions(body, say, logger):
    logger.info(body)
    say("What's up?")


@app.message("What")
def handle_matched_messages(event, logger):
    logger.info(f"message matched: {event['text']}")


@app.event("message")
def handle_messages(event, logger):
    logger.info(f"subtype: {event.get('subytype')}")


api = falcon.API()
resource = SlackAppResource(app)
api.add_route("/slack/events", resource)

# # -- OAuth flow -- #
# pip install -r requirements.txt
# export SLACK_SIGNING_SECRET=***
# export SLACK_BOT_TOKEN=xoxb-***
# export SLACK_CLIENT_ID=111.111
# export SLACK_CLIENT_SECRET=***
# export SLACK_SCOPES=app_mentions:read,channels:history,im:history,chat:write
# gunicorn oauth_app:api --reload -b 0.0.0.0:3000
api.add_route("/slack/install", resource)
api.add_route("/slack/oauth_redirect", resource)
