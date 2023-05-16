import logging

logging.basicConfig(level=logging.DEBUG)

from slack_bolt import App
from slack_bolt.adapter.cherrypy import SlackRequestHandler

app = App()


@app.middleware  # or app.use(log_request)
def log_request(logger, body, next):
    logger.debug(body)
    return next()


@app.command("/hello-bolt-python")
def hello_command(ack):
    ack("Hi from CherryPy")


@app.event("app_mention")
def event_test(body, say, logger):
    logger.info(body)
    say("What's up?")


import cherrypy

handler = SlackRequestHandler(app)


class SlackApp(object):
    @cherrypy.expose
    @cherrypy.tools.slack_in()
    def events(self, **kwargs):
        return handler.handle()


if __name__ == "__main__":
    cherrypy.config.update({"server.socket_port": 3000})
    cherrypy.quickstart(SlackApp(), "/slack")

# pip install -r requirements.txt
# export SLACK_SIGNING_SECRET=***
# export SLACK_BOT_TOKEN=xoxb-***
# python app.py
