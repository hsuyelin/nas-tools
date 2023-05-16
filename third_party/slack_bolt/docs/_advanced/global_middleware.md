---
title: Global middleware
lang: en
slug: global-middleware
order: 8
---

<div class="section-content">
Global middleware is run for all incoming requests, before any listener middleware. You can add any number of global middleware to your app by passing middleware functions to `app.use()`. Middleware functions are called with the same arguments as listeners, with an additional `next()` function.

Both global and listener middleware must call `next()` to pass control of the execution chain to the next middleware. 
</div>

<div>
<span class="annotation">Refer to <a href="https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html" target="_blank">the module document</a> to learn the available listener arguments.</span>
```python
@app.use
def auth_acme(client, context, logger, payload, next):
    slack_user_id = payload["user"]
    help_channel_id = "C12345"

    try:
        # Look up user in external system using their Slack user ID
        user = acme.lookup_by_id(slack_user_id)
        # Add that to context
        context["user"] = user
    except Exception:
        client.chat_postEphemeral(
            channel=payload["channel"],
            user=slack_user_id,
            text=f"Sorry <@{slack_user_id}>, you aren't registered in Acme or there was an error with authentication. Please post in <#{help_channel_id}> for assistance"
        )

    # Pass control to the next middleware
    next()
```
</div>
