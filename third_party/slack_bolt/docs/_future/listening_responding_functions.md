---
title: Listening & responding to functions
lang: en
slug: functions
order: 5
layout: future
---

<div class="section-content">

Your app can use the `function()` method to listen to incoming function requests. The method requires a function `callback_id` of type `str`. This `callback_id` must also be defined in your [Function](/bolt-python/future/concepts#manifest-functions) definition. Functions must eventually be completed with the `complete()` function to inform Slack that your app has processed the function request. `complete()` requires **one of two** keyword arguments: `outputs` or `error`. There are two ways to complete a Function with `complete()`:

* `outputs` of type `dict` completes your function **successfully** and provides a dictionary containing the outputs of your function as defined in the app's manifest.
* `error` of type `str` completes your function **unsuccessfully** and provides a message containing information regarding why your function was not successful.

</div>

<div>
<span class="annotation">Refer to <a href="https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html" target="_blank">the module document</a> to learn the available listener arguments.</span>
```python
# The sample function simply outputs an input
@app.function("sample_function")
def sample_func(event: dict, complete: Complete):
    try:
        message = event["inputs"]["message"]
        complete(
            outputs={
                "updatedMsg": f":wave: You submitted the following message: \n\n>{message}"
            }
        )
    except Exception as e:
        complete(error=f"Cannot submit the message: {e}")
        raise e
```
</div>

<details class="secondary-wrapper">
<summary markdown="0">
<h4 class="secondary-header">Function Interactivity</h4>
</summary>

<div class="secondary-content">

The `function()` method returns a `SlackFunction` decorator object. This object can be used by your app to set up interactive listeners such as [actions](/bolt-python/concepts#action-respond) and [views](/bolt-python/concepts#view_submissions). These listeners listen to events created during the handling of your `function` event. Additionally, they will only be called when a user interacts with a block element that has the following attributes:

* It was created during the handling of a `function` event.
* The `action_id` matches the interactive listeners `action_id`.

These listeners behave similarly to the ones assigned directly to your app. The notable difference is that `complete()` must be called once your function is completed.

</div>

```python
# Your listener will be called when your function "sample_function" is triggered from a workflow
# When triggered a message containing a button with an action_id "approve_button" is posted
@app.function("sample_function")
def sample_func(event: dict, complete: Complete):
    try:
        client.chat_postMessage(
            channel="a-channel-id",
            text="A new button appears",
            blocks=[
                {
                    "type": "actions",
                    "block_id": "approve-button",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Click",
                            },
                            "action_id": "sample_action",
                            "style": "primary",
                        },
                    ],
                },
            ],
        )
    except Exception as e:
        complete(error=f"Cannot post the message: {e}")
        raise e

# Your listener will be called when a block element
#   - Created by your "sample_func"
#   - With the action_id "sample_action"
# is triggered
@sample_func.action("sample_action")
def update_message(ack, body, client, complete):
    try:
        ack()
        if "container" in body and "message_ts" in body["container"]:
            client.reactions_add(
                name="white_check_mark",
                channel=body["channel"]["id"],
                timestamp=body["container"]["message_ts"],
            )
        complete()
    except Exception as e:
        logger.error(e)
        complete(error=f"Cannot react to message: {e}")
        raise e
```

</details>
