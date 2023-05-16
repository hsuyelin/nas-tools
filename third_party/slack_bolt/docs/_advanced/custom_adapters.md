---
title: Custom adapters
lang: en
slug: custom-adapters
order: 1
---

<div class="section-content">
[Adapters](#adapters) are flexible and can be adjusted based on the framework you prefer. There are two necessary components of adapters:

- `__init__(app: App)`: Constructor that accepts and stores an instance of the Bolt `App`.
- `handle(req: Request)`: Function (typically named `handle()`) that receives incoming Slack requests, parses them to conform to an instance of [`BoltRequest`](https://github.com/slackapi/bolt-python/blob/main/slack_bolt/request/request.py), then dispatches them to the stored Bolt app.

`BoltRequest` instantiation accepts four parameters:

| Parameter | Description | Required? |
|-----------|-------------|-----------|
| `body: str` | The raw request body | **Yes** |
| `query: any` | The query string data | No |
| `headers: Dict[str, Union[str, List[str]]]` | Request headers | No |
| `context: BoltContext` | Any context for the request | No |

Your adapter will return [an instance of `BoltResponse`](https://github.com/slackapi/bolt-python/blob/main/slack_bolt/response/response.py) from the Bolt app.

For more in-depth examples of custom adapters, look at the implementations of the [built-in adapters](https://github.com/slackapi/bolt-python/tree/main/slack_bolt/adapter).
</div>

```python
# Necessary imports for Flask
from flask import Request, Response, make_response

from slack_bolt.app import App
from slack_bolt.request import BoltRequest
from slack_bolt.response import BoltResponse

# This example is a simplified version of the Flask adapter
# For a more detailed, complete example, look in the adapter folder
# github.com/slackapi/bolt-python/blob/main/slack_bolt/adapter/flask/handler.py

# Takes in an HTTP request and converts it to a standard BoltRequest
def to_bolt_request(req: Request) -> BoltRequest:
    return BoltRequest(
        body=req.get_data(as_text=True),
        query=req.query_string.decode("utf-8"),
        headers=req.headers,
    )

# Takes in a BoltResponse and converts it to a standard Flask response
def to_flask_response(bolt_resp: BoltResponse) -> Response:
    resp: Response = make_response(bolt_resp.body, bolt_resp.status)
    for k, values in bolt_resp.headers.items():
        for v in values:
            resp.headers.add_header(k, v)
    return resp

# Instantiated from your app
# Accepts a Flask app
class SlackRequestHandler:
    def __init__(self, app: App):
        self.app = app

    # handle() will be called from your Flask app 
    # when you receive a request from Slack
    def handle(self, req: Request) -> Response:
        # This example does not cover OAuth
        if req.method == "POST":
            # Dispatch the request for Bolt to handle and route
            bolt_resp: BoltResponse = self.app.dispatch(to_bolt_request(req))
            return to_flask_response(bolt_resp)

        return make_response("Not Found", 404)
```
