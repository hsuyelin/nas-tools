import logging
import os
from slack_bolt import App, BoltResponse
from slack_bolt.oauth.callback_options import CallbackOptions, SuccessArgs, FailureArgs
from slack_bolt.oauth.oauth_settings import OAuthSettings

from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.oauth.state_store import FileOAuthStateStore

logging.basicConfig(level=logging.DEBUG)


def success(args: SuccessArgs) -> BoltResponse:
    # Do anything here ...
    # Call the default handler to return HTTP response
    return args.default.success(args)
    # return BoltResponse(status=200, body="Thanks!")


def failure(args: FailureArgs) -> BoltResponse:
    return BoltResponse(status=args.suggested_status_code, body=args.reason)


app = App(
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    installation_store=FileInstallationStore(),
    oauth_settings=OAuthSettings(
        client_id=os.environ.get("SLACK_CLIENT_ID"),
        client_secret=os.environ.get("SLACK_CLIENT_SECRET"),
        scopes=["app_mentions:read", "channels:history", "im:history", "chat:write"],
        user_scopes=[],
        redirect_uri=None,
        install_path="/slack/install",
        redirect_uri_path="/slack/oauth_redirect",
        state_store=FileOAuthStateStore(expiration_seconds=600),
        callback_options=CallbackOptions(success=success, failure=failure),
    ),
)


@app.command("/hello-bolt-python")
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
# python oauth_app.py
