import logging

logging.basicConfig(level=logging.DEBUG)

from slack_bolt import App
from slack_bolt.oauth import OAuthFlow

app = App(
    oauth_flow=OAuthFlow.sqlite3(
        database="./slackapp.db",
        token_rotation_expiration_minutes=60 * 24,  # for testing
    ),
    installation_store_bot_only=True,
)


@app.event("app_mention")
def handle_app_mentions(body, say, logger):
    logger.info(body)
    say("What's up?")


@app.command("/token-rotation-modal")
def handle_some_command(ack, body, logger):
    ack()
    logger.info(body)


if __name__ == "__main__":
    app.start(3000)

# pip install slack_bolt
# export SLACK_SIGNING_SECRET=***
# export SLACK_BOT_TOKEN=xoxb-***
# export SLACK_CLIENT_ID=111.111
# export SLACK_CLIENT_SECRET=***
# export SLACK_SCOPES=app_mentions:read,channels:history,im:history,chat:write
# python oauth_app.py
