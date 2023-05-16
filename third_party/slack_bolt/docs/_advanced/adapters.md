---
title: Adapters
lang: en
slug: adapters
order: 0
---

<div class="section-content">
Adapters are responsible for handling and parsing incoming requests from Slack to conform to <a href="https://github.com/slackapi/bolt-python/blob/main/slack_bolt/request/request.py">`BoltRequest`</a>, then dispatching those requests to your Bolt app.

By default, Bolt will use the built-in <a href="https://docs.python.org/3/library/http.server.html">`HTTPServer`</a> adapter. While this is okay for local development, <b>it is not recommended for production</b>. Bolt for Python includes a collection of built-in adapters that can be imported and used with your app. The built-in adapters support a variety of popular Python frameworks including Flask, Django, and Starlette among others. Adapters support the use of any production-ready web server of your choice.

To use an adapter, you'll create an app with the framework of your choosing and import its corresponding adapter. Then you'll initialize the adapter instance and call its function that handles and parses incoming requests.

The full list adapters, as well as configuration and sample usage, can be found within the repository's <a href="https://github.com/slackapi/bolt-python/tree/main/examples">`examples` folder</a>.
</div>

```python
from slack_bolt import App
app = App(
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    token=os.environ.get("SLACK_BOT_TOKEN")
)

# There is nothing specific to Flask here!
# App is completely framework/runtime agnostic
@app.command("/hello-bolt")
def hello(body, ack):
    ack(f"Hi <@{body['user_id']}>!")

# Initialize Flask app
from flask import Flask, request
flask_app = Flask(__name__)

# SlackRequestHandler translates WSGI requests to Bolt's interface
# and builds WSGI response from Bolt's response.
from slack_bolt.adapter.flask import SlackRequestHandler
handler = SlackRequestHandler(app)

# Register routes to Flask app
@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    # handler runs App's dispatch method
    return handler.handle(request)
```
