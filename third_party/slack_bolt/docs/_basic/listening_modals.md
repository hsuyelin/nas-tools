---
title: Listening for view submissions
lang: en
slug: view_submissions
order: 12
---

<div class="section-content">

If a <a href="https://api.slack.com/reference/block-kit/views">view payload</a> contains any input blocks, you must listen to `view_submission` requests to receive their values. To listen to `view_submission` requests, you can use the built-in `view()` method. `view()` requires a `callback_id` of type `str` or `re.Pattern`.

You can access the value of the `input` blocks by accessing the `state` object. `state` contains a `values` object that uses the `block_id` and unique `action_id` to store the input values.

---

##### Update views on submission

To update a view in response to a `view_submission` event, you may pass a `response_action` of type `update` with a newly composed `view` to display in your acknowledgement.

```python
# Update the view on submission 
@app.view("view_1")
def handle_submission(ack, body):
    ack(response_action="update", view=build_new_view(body))
```
Similarly, there are options for [displaying errors](https://api.slack.com/surfaces/modals/using#displaying_errors) in response to view submissions.
Read more about view submissions in our <a href="https://api.slack.com/surfaces/modals/using#handling_submissions">API documentation</a>.

---

##### Handling views on close

When listening for `view_closed` requests, you must pass `callback_id` and add a `notify_on_close` property to the view during creation. See below for an example of this:

See the <a href="https://api.slack.com/surfaces/modals/using#modal_cancellations">API documentation</a> for more information about view_closed.

```python

client.views_open(
    trigger_id=body.get("trigger_id"),
    view={
        "type": "modal",
        "callback_id": "modal-id",  # Used when calling view_closed
        "title": {
            "type": "plain_text",
            "text": "Modal title"
        },
        "blocks": [],
        "close": {
            "type": "plain_text",
            "text": "Cancel"
        },
        "notify_on_close": True,  # This attribute is required
    }
)

# Handle a view_closed request
@app.view_closed("modal-id")
def handle_view_closed(ack, body, logger):
    ack()
    logger.info(body)
```

</div>

<div>
<span class="annotation">Refer to <a href="https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html" target="_blank">the module document</a> to learn the available listener arguments.</span>
```python
# Handle a view_submission request
@app.view("view_1")
def handle_submission(ack, body, client, view, logger):
    # Assume there's an input block with `input_c` as the block_id and `dreamy_input`
    hopes_and_dreams = view["state"]["values"]["input_c"]["dreamy_input"]
    user = body["user"]["id"]
    # Validate the inputs
    errors = {}
    if hopes_and_dreams is not None and len(hopes_and_dreams) <= 5:
        errors["input_c"] = "The value must be longer than 5 characters"
    if len(errors) > 0:
        ack(response_action="errors", errors=errors)
        return
    # Acknowledge the view_submission request and close the modal
    ack()
    # Do whatever you want with the input data - here we're saving it to a DB
    # then sending the user a verification of their submission

    # Message to send user
    msg = ""
    try:
        # Save to DB
        msg = f"Your submission of {hopes_and_dreams} was successful"
    except Exception as e:
        # Handle error
        msg = "There was an error with your submission"

    # Message the user
    try:
        client.chat_postMessage(channel=user, text=msg)
    except e:
        logger.exception(f"Failed to post a message {e}")
```
</div>