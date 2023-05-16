---
title: Lazy listeners (FaaS)
lang: en
slug: lazy-listeners
order: 10
---

<div class="section-content">
Lazy Listeners are a feature which make it easier to deploy Slack apps to FaaS (Function-as-a-Service) environments. Please note that this feature is only available in Bolt for Python, and we are not planning to add the same to other Bolt frameworks.

Typically when handling actions, commands, shortcuts, options and view submissions, you must acknowledge the request from Slack by calling `ack()` within 3 seconds. Calling `ack()` results in sending an HTTP 200 OK response to Slack, letting Slack know that you're handling the response. We normally encourage you to do this as the very first step in your handler function. 

However, when running your app on FaaS or similar runtimes which **do not allow you to run threads or processes after returning an HTTP response**, we cannot follow the typical pattern of acknowledgement first, processing later. To work with these runtimes, set the `process_before_response` flag to `True`. When this flag is true, the Bolt framework holds off sending an HTTP response until all the things in a listener function are done. You need to complete your processing within 3 seconds or you will run into errors with Slack timeouts. Note that in the case of events, while the listener doesn't need to explicitly call the `ack()` method, it still needs to complete its function within 3 seconds as well.

To allow you to still run more time-consuming processes as part of your handler, we've added a lazy listener function mechanism. Rather than acting as a decorator, a lazy listener accepts two keyword args:
* `ack: Callable`: Responsible for calling `ack()` within 3 seconds
* `lazy: List[Callable]`: Responsible for handling time-consuming processes related to the request. The lazy function does not have access to `ack()`.
</div>

```python
def respond_to_slack_within_3_seconds(body, ack):
    text = body.get("text")
    if text is None or len(text) == 0:
        ack(f":x: Usage: /start-process (description here)")
    else:
        ack(f"Accepted! (task: {body['text']})")

import time
def run_long_process(respond, body):
    time.sleep(5)  # longer than 3 seconds
    respond(f"Completed! (task: {body['text']})")

app.command("/start-process")(
    # ack() is still called within 3 seconds
    ack=respond_to_slack_within_3_seconds,
    # Lazy function is responsible for processing the event
    lazy=[run_long_process]
)
```

<details class="secondary-wrapper">
<summary class="section-head" markdown="0">
<h4 class="section-head">Example with AWS Lambda</h4>
</summary>

<div class="secondary-content" markdown="0">
This example deploys the code to [AWS Lambda](https://aws.amazon.com/lambda/). There are more examples within the [`examples` folder](https://github.com/slackapi/bolt-python/tree/main/examples/aws_lambda).

```bash
pip install slack_bolt
# Save the source code as main.py
# and refer handler as `handler: main.handler` in config.yaml

# https://pypi.org/project/python-lambda/
pip install python-lambda

# Configure config.yml properly
# lambda:InvokeFunction & lambda:GetFunction are required for running lazy listeners
export SLACK_SIGNING_SECRET=***
export SLACK_BOT_TOKEN=xoxb-***
echo 'slack_bolt' > requirements.txt
lambda deploy --config-file config.yaml --requirements requirements.txt
```
</div>

```python
from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler

# process_before_response must be True when running on FaaS
app = App(process_before_response=True)

def respond_to_slack_within_3_seconds(body, ack):
    text = body.get("text")
    if text is None or len(text) == 0:
        ack(":x: Usage: /start-process (description here)")
    else:
        ack(f"Accepted! (task: {body['text']})")

import time
def run_long_process(respond, body):
    time.sleep(5)  # longer than 3 seconds
    respond(f"Completed! (task: {body['text']})")

app.command("/start-process")(
    ack=respond_to_slack_within_3_seconds,  # responsible for calling `ack()`
    lazy=[run_long_process]  # unable to call `ack()` / can have multiple functions
)

def handler(event, context):
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)
```

Please note that the following IAM permissions would be required for running this example app.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "lambda:InvokeFunction",
                "lambda:GetFunction"
            ],
            "Resource": "*"
        }
    ]
}
```
</details>
