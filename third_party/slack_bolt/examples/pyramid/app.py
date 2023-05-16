import logging
from slack_bolt import App
from slack_bolt.adapter.pyramid.handler import SlackRequestHandler

logging.basicConfig(level=logging.DEBUG)
app = App()


@app.event("app_mention")
def event_test(body, say, logger):
    logger.info(body)
    say("What's up?")


handler = SlackRequestHandler(app)

if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    from pyramid.config import Configurator

    with Configurator() as config:
        config.add_route("slack_events", "/slack/events")
        config.add_view(handler.handle, route_name="slack_events", request_method="POST")
        pyramid_app = config.make_wsgi_app()
    server = make_server("0.0.0.0", 3000, pyramid_app)
    server.serve_forever()

# export SLACK_SIGNING_SECRET=***
# export SLACK_BOT_TOKEN=xoxb-***
# python app.py
