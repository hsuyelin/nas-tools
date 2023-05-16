---
title: Using the Web API
lang: en
slug: web-api
order: 4
---

<div class="section-content">
You can call [any Web API method](https://api.slack.com/methods) using the [`WebClient`](https://slack.dev/python-slack-sdk/basic_usage.html) provided to your Bolt app as either `app.client` or `client` in middleware/listener arguments (given that your app has the appropriate scopes). When you call one the client's methods, it returns a `SlackResponse` which contains the response from Slack.

The token used to initialize Bolt can be found in the `context` object, which is required to call most Web API methods.

</div>

<div>
<span class="annotation">Refer to <a href="https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html" target="_blank">the module document</a> to learn the available listener arguments.</span>
```python
@app.message("wake me up")
def say_hello(client, message):
    # Unix Epoch time for September 30, 2020 11:59:59 PM
    when_september_ends = 1601510399
    channel_id = message["channel"]
    client.chat_scheduleMessage(
        channel=channel_id,
        post_at=when_september_ends,
        text="Summer has come and passed"
    )
```
</div>