---
title: Listening and responding to options
lang: en
slug: options
order: 14
---

<div class="section-content">
The `options()` method listens for incoming option request payloads from Slack. [Similar to `action()`](#action-listening),
an `action_id` or constraints object is required. In order to load external data into your select menus, you must provide an options load URL in your app configuration, appended with `/slack/events`.

While it's recommended to use `action_id` for `external_select` menus, dialogs do not support Block Kit so you'll have to use the constraints object to filter on a `callback_id`.

To respond to options requests, you'll need to call `ack()` with a valid `options` or `option_groups` list. Both [external select response examples](https://api.slack.com/reference/messaging/block-elements#external-select) and [dialog response examples](https://api.slack.com/dialogs#dynamic_select_elements_external) can be found on our API site.

Additionally, you may want to apply filtering logic to the returned options based on user input. This can be accomplished by using the `payload` argument to your options listener and checking for the contents of the `value` property within it. Based on the `value` you can return different options. All listeners and middleware handlers in Bolt for Python have access to [many useful arguments](https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html) - be sure to check them out!
</div>

<div>
<span class="annotation">Refer to <a href="https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html" target="_blank">the module document</a> to learn the available listener arguments.</span>
```python
# Example of responding to an external_select options request
@app.options("external_action")
def show_options(ack, payload):
    options = [
        {
            "text": {"type": "plain_text", "text": "Option 1"},
            "value": "1-1",
        },
        {
            "text": {"type": "plain_text", "text": "Option 2"},
            "value": "1-2",
        },
    ]
    keyword = payload.get("value")
    if keyword is not None and len(keyword) > 0:
        options = [o for o in options if keyword in o["text"]["text"]]
    ack(options=options)
```
</div>
