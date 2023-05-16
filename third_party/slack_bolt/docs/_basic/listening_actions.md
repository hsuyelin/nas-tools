---
title: Listening to actions
lang: en
slug: action-listening
order: 5
---

<div class="section-content">
Your app can listen to user actions, like button clicks, and menu selects, using the `action` method.

Actions can be filtered on an `action_id` of type `str` or `re.Pattern`. `action_id`s act as unique identifiers for interactive components on the Slack platform.

You'll notice in all `action()` examples, `ack()` is used. It is required to call the `ack()` function within an action listener to acknowledge that the request was received from Slack. This is discussed in the [acknowledging requests section](#acknowledge).

</div>

<div>
<span class="annotation">Refer to <a href="https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html" target="_blank">the module document</a> to learn the available listener arguments.</span>
```python
# Your listener will be called every time a block element with the action_id "approve_button" is triggered
@app.action("approve_button")
def update_message(ack):
    ack()
    # Update the message to reflect the action
```
</div>

<details class="secondary-wrapper">
<summary class="section-head" markdown="0">
<h4 class="section-head">Listening to actions using a constraint object</h4>
</summary>

<div class="secondary-content" markdown="0">

You can use a constraints object to listen to `callback_id`s, `block_id`s, and `action_id`s (or any combination of them). Constraints in the object can be of type `str` or `re.Pattern`.

</div>

```python
# Your function will only be called when the action_id matches 'select_user' AND the block_id matches 'assign_ticket'
@app.action({
    "block_id": "assign_ticket",
    "action_id": "select_user"
})
def update_message(ack, body, client):
    ack()

    if "container" in body and "message_ts" in body["container"]:
        client.reactions_add(
            name="white_check_mark",
            channel=body["channel"]["id"],
            timestamp=body["container"]["message_ts"],
        )
```

</details>
