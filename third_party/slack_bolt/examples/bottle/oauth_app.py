import logging
from slack_bolt import App
from slack_bolt.adapter.bottle import SlackRequestHandler

logging.basicConfig(level=logging.DEBUG)
app = App()


@app.middleware  # or app.use(log_request)
def log_request(logger, body, next):
    logger.debug(body)
    return next()


@app.event("app_mention")
def event_test(body, say, logger):
    logger.info(body)
    say("What's up?")


from bottle import get, post, request, response, run

handler = SlackRequestHandler(app)


@post("/slack/events")
def slack_events():
    return handler.handle(request, response)


@get("/slack/install")
def install():
    return handler.handle(request, response)


@get("/slack/oauth_redirect")
def oauth_redirect():
    return handler.handle(request, response)


if __name__ == "__main__":
    run(host="0.0.0.0", port=3000, reloader=True)

# pip install -r requirements.txt

# # -- OAuth flow -- #
# export SLACK_SIGNING_SECRET=***
# export SLACK_BOT_TOKEN=xoxb-***
# export SLACK_CLIENT_ID=111.111
# export SLACK_CLIENT_SECRET=***
# export SLACK_SCOPES=app_mentions:read,chat:write

# python oauth_app.py
