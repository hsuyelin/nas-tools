import logging
from slack_bolt import App

logging.basicConfig(level=logging.DEBUG)
app = App()


@app.event("app_mention")
def event_test(body, say, logger):
    logger.info(body)
    say("What's up?")


@app.command("/hello-bolt-python")
# or app.command(re.compile(r"/hello-.+"))(test_command)
def test_command(body, respond, client, ack, logger):
    logger.info(body)
    ack("Thanks!")

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
    return ack()


@app.action("a")
def button_click(logger, body, ack, respond):
    logger.info(body)
    respond("respond!")
    ack()


if __name__ == "__main__":
    app.start(3000)

# pip install slack_bolt
# export SLACK_SIGNING_SECRET=***
# export SLACK_CLIENT_ID=111.111
# export SLACK_CLIENT_SECRET=***
# export SLACK_SCOPES=app_mentions:read,channels:history,im:history,chat:write
# python oauth_app.py
