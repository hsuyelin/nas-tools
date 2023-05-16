---
title: Updating and pushing views
lang: en
slug: updating-pushing-views
order: 11
---

<div class="section-content">

Modals contain a stack of views. When you call <a href="https://api.slack.com/methods/views.open">`views_open`</a>, you add the root view to the modal. After the initial call, you can dynamically update a view by calling <a href="https://api.slack.com/methods/views.update">`views_update`</a>, or stack a new view on top of the root view by calling <a href="https://api.slack.com/methods/views.push">`views_push`</a>.

**`views_update`**<br>
To update a view, you can use the built-in client to call `views_update` with the `view_id` that was generated when you opened the view, and a new `view` including the updated `blocks` list. If you're updating the view when a user interacts with an element inside of an existing view, the `view_id` will be available in the `body` of the request.

**`views_push`**<br>
To push a new view onto the view stack, you can use the built-in client to call `views_push` with a valid `trigger_id` a new <a href="https://api.slack.com/reference/block-kit/views">view payload</a>. The arguments for `views_push` is the same as <a href="#creating-modals">opening modals</a>. After you open a modal, you may only push two additional views onto the view stack.

Learn more about updating and pushing views in our <a href="https://api.slack.com/surfaces/modals/using#modifying">API documentation</a>.

</div>

<div>
<span class="annotation">Refer to <a href="https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html" target="_blank">the module document</a> to learn the available listener arguments.</span>
```python
# Listen for a button invocation with action_id `button_abc` (assume it's inside of a modal)
@app.action("button_abc")
def update_modal(ack, body, client):
    # Acknowledge the button request
    ack()
    # Call views_update with the built-in client
    client.views_update(
        # Pass the view_id
        view_id=body["view"]["id"],
        # String that represents view state to protect against race conditions
        hash=body["view"]["hash"],
        # View payload with updated blocks
        view={
            "type": "modal",
            # View identifier
            "callback_id": "view_1",
            "title": {"type": "plain_text", "text": "Updated modal"},
            "blocks": [
                {
                    "type": "section",
                    "text": {"type": "plain_text", "text": "You updated the modal!"}
                },
                {
                    "type": "image",
                    "image_url": "https://media.giphy.com/media/SVZGEcYt7brkFUyU90/giphy.gif",
                    "alt_text": "Yay! The modal was updated"
                }
            ]
        }
    )
```
</div>