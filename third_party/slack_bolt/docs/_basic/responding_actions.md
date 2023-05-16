---
title: Responding to actions
lang: en
slug: action-respond
order: 6
---

<div class="section-content">

There are two main ways to respond to actions. The first (and most common) way is to use `say()`, which sends a message back to the conversation where the incoming request took place.

The second way to respond to actions is using `respond()`, which is a utility to use the `response_url` associated with the action.

</div>

<div>
<span class="annotation">Refer to <a href="https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html" target="_blank">the module document</a> to learn the available listener arguments.</span>
```python
# Your listener will be called every time an interactive component with the action_id “approve_button” is triggered
@app.action("approve_button")
def approve_request(ack, say):
    # Acknowledge action request
    ack()
    say("Request approved 👍")
```
</div>

<details class="secondary-wrapper">
<summary class="section-head" markdown="0">
<h4 class="section-head">Using respond()</h4>
</summary>

<div class="secondary-content" markdown="0">

Since `respond()` is a utility for calling the `response_url`, it behaves in the same way. You can pass [all the message payload properties](https://api.slack.com/reference/messaging/payload) as keyword arguments along with optional properties like `response_type` (which has a value of `"in_channel"` or `"ephemeral"`), `replace_original`, `delete_original`, `unfurl_links`, and `unfurl_media`. With that, your app can send a new message payload that will be published back to the source of the original interaction.

</div>

```python
# Listens to actions triggered with action_id of “user_select”
@app.action("user_select")
def select_user(ack, action, respond):
    ack()
    respond(f"You selected <@{action['selected_user']}>")
```

</details>
