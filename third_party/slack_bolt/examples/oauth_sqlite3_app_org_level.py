import logging

logging.basicConfig(level=logging.DEBUG)

from slack_bolt import App, BoltContext
from slack_bolt.oauth import OAuthFlow
from slack_sdk import WebClient


app = App(oauth_flow=OAuthFlow.sqlite3(database="./slackapp.db"))


@app.use
def dump(context, next, logger):
    logger.info(context)
    next()


@app.use
def call_apis_with_team_id(context: BoltContext, client: WebClient, next):
    # client.users_list()
    client.bots_info(bot=context.bot_id)
    next()


@app.event("app_mention")
def handle_app_mentions(body, say, logger):
    logger.info(body)
    say("What's up?")


@app.command("/org-level-command")
def command(ack):
    ack("I got it!")


@app.shortcut("org-level-shortcut")
def shortcut(ack):
    ack()


@app.event("team_access_granted")
def team_access_granted(event):
    pass


@app.event("team_access_revoked")
def team_access_revoked(event):
    pass


if __name__ == "__main__":
    app.start(3000)

# pip install slack_bolt
# export SLACK_SIGNING_SECRET=***
# export SLACK_BOT_TOKEN=xoxb-***
# export SLACK_CLIENT_ID=111.111
# export SLACK_CLIENT_SECRET=***
# export SLACK_SCOPES=app_mentions:read,channels:history,im:history,chat:write
# python oauth_app.py
