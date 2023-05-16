---
title: Listener middleware
lang: en
slug: listener-middleware
order: 7
---

<div class="section-content">
Listener middleware is only run for the listener in which it's passed. You can pass any number of middleware functions to the listener using the `middleware` parameter, which must be a list that contains one to many middleware functions.

If your listener middleware is a quite simple one, you can use a listener matcher, which returns `bool` value (`True` for proceeding) instead of requiring `next()` method call.
</div>

<div>
<span class="annotation">Refer to <a href="https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html" target="_blank">the module document</a> to learn the available listener arguments.</span>

```python
# Listener middleware which filters out messages with "bot_message" subtype
def no_bot_messages(message, next):
    subtype = message.get("subtype")
    if subtype != "bot_message":
       next()

# This listener only receives messages from humans
@app.event(event="message", middleware=[no_bot_messages])
def log_message(logger, event):
    logger.info(f"(MSG) User: {event['user']}\nMessage: {event['text']}")

# Listener matchers: simplified version of listener middleware
def no_bot_messages(message) -> bool:
    return message.get("subtype") != "bot_message"

@app.event(
    event="message", 
    matchers=[no_bot_messages]
    # or matchers=[lambda message: message.get("subtype") != "bot_message"]
)
def log_message(logger, event):
    logger.info(f"(MSG) User: {event['user']}\nMessage: {event['text']}")
```
</div>