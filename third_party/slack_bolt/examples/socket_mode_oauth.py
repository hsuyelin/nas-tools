import logging

logging.basicConfig(level=logging.DEBUG)

import os
from slack_bolt.app import App
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_bolt.adapter.socket_mode import SocketModeHandler

app = App(
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
    oauth_settings=OAuthSettings(
        client_id=os.environ["SLACK_CLIENT_ID"],
        client_secret=os.environ["SLACK_CLIENT_SECRET"],
        scopes=os.environ["SLACK_SCOPES"].split(","),
    ),
)


@app.command("/hello-socket-mode")
def hello_command(ack, body):
    user_id = body["user_id"]
    ack(f"Hi <@{user_id}>!")


@app.event("app_mention")
def event_test(event, say):
    say(f"Hi there, <@{event['user']}>!")


def ack_shortcut(ack):
    ack()


def open_modal(body, client):
    client.views_open(
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
def external_data_source_handler(ack, body):
    keyword = body.get("value")
    if keyword is not None and len(keyword) > 0:
        options = [o for o in all_options if keyword in o["text"]["text"]]
        ack(options=options)
    else:
        ack(options=all_options)


@app.view("socket_modal_submission")
def submission(ack):
    ack()


if __name__ == "__main__":
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).connect()
    app.start()

    # export SLACK_APP_TOKEN=
    # export SLACK_SIGNING_SECRET=
    # export SLACK_CLIENT_ID=
    # export SLACK_CLIENT_SECRET=
    # export SLACK_SCOPES=
    # pip install .[optional]
    # pip install slack_bolt
    # python socket_mode_oauth.py
