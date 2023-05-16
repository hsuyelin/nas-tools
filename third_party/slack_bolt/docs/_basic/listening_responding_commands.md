---
title: Listening and responding to commands
lang: en
slug: commands
order: 9
---

<div class="section-content">

Your app can use the `command()` method to listen to incoming slash command requests. The method requires a `command_name` of type `str`.

Commands must be acknowledged with `ack()` to inform Slack your app has received the request.

There are two ways to respond to slash commands. The first way is to use `say()`, which accepts a string or JSON payload. The second is `respond()` which is a utility for the `response_url`. These are explained in more depth in the [responding to actions](#action-respond) section.

When setting up commands within your app configuration, you'll append `/slack/events` to your request URL.

</div>

<div>
<span class="annotation">Refer to <a href="https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html" target="_blank">the module document</a> to learn the available listener arguments.</span>
```python
# The echo command simply echoes on command
@app.command("/echo")
def repeat_text(ack, respond, command):
    # Acknowledge command request
    ack()
    respond(f"{command['text']}")
```
</div>