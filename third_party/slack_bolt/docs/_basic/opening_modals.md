---
title: Opening modals
lang: en
slug: opening-modals
order: 10
---

<div class="section-content">

<a href="https://api.slack.com/block-kit/surfaces/modals">Modals</a> are focused surfaces that allow you to collect user data and display dynamic information. You can open a modal by passing a valid `trigger_id` and a <a href="https://api.slack.com/reference/block-kit/views">view payload</a> to the built-in client's <a href="https://api.slack.com/methods/views.open">`views.open`</a> method.

Your app receives `trigger_id`s in payloads sent to your Request URL that are triggered by user invocations, like a shortcut, button press, or interaction with a select menu.

Read more about modal composition in the <a href="https://api.slack.com/surfaces/modals/using#composing_views">API documentation</a>.

</div>

<div>
<span class="annotation">Refer to <a href="https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html" target="_blank">the module document</a> to learn the available listener arguments.</span>
```python
# Listen for a shortcut invocation
@app.shortcut("open_modal")
def open_modal(ack, body, client):
    # Acknowledge the command request
    ack()
    # Call views_open with the built-in client
    client.views_open(
        # Pass a valid trigger_id within 3 seconds of receiving it
        trigger_id=body["trigger_id"],
        # View payload
        view={
            "type": "modal",
            # View identifier
            "callback_id": "view_1",
            "title": {"type": "plain_text", "text": "My App"},
            "submit": {"type": "plain_text", "text": "Submit"},
            "blocks": [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "Welcome to a modal with _blocks_"},
                    "accessory": {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Click me!"},
                        "action_id": "button_abc"
                    }
                },
                {
                    "type": "input",
                    "block_id": "input_c",
                    "label": {"type": "plain_text", "text": "What are your hopes and dreams?"},
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "dreamy_input",
                        "multiline": True
                    }
                }
            ]
        }
    )
```
</div>