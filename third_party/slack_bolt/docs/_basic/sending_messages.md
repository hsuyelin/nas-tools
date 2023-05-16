---
title: Sending messages
lang: en
slug: message-sending
order: 2
---

<div class="section-content">

Within your listener function, `say()` is available whenever there is an associated conversation (for example, a conversation where the event or action which triggered the listener occurred). `say()` accepts a string to post simple messages and JSON payloads to send more complex messages. The message payload you pass in will be sent to the associated conversation.

In the case that you'd like to send a message outside of a listener or you want to do something more advanced (like handle specific errors), you can call `client.chat_postMessage` [using the client attached to your Bolt instance](#web-api).

</div>

<div>
<span class="annotation">Refer to <a href="https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html" target="_blank">the module document</a> to learn the available listener arguments.</span>
```python
# Listens for messages containing "knock knock" and responds with an italicized "who's there?"
@app.message("knock knock")
def ask_who(message, say):
    say("_Who's there?_")
```
</div>

<details class="secondary-wrapper">
<summary markdown="0">
<h4 class="secondary-header">Sending a message with blocks</h4>
</summary>

<div class="secondary-content" markdown="0">
`say()` accepts more complex message payloads to make it easy to add functionality and structure to your messages.

To explore adding rich message layouts to your app, read through [the guide on our API site](https://api.slack.com/messaging/composing/layouts) and look through templates of common app flows [in the Block Kit Builder](https://api.slack.com/tools/block-kit-builder?template=1).

</div>

```python
# Sends a section block with datepicker when someone reacts with a 📅 emoji
@app.event("reaction_added")
def show_datepicker(event, say):
    reaction = event["reaction"]
    if reaction == "calendar":
        blocks = [{
          "type": "section",
          "text": {"type": "mrkdwn", "text": "Pick a date for me to remind you"},
          "accessory": {
              "type": "datepicker",
              "action_id": "datepicker_remind",
              "initial_date": "2020-05-04",
              "placeholder": {"type": "plain_text", "text": "Select a date"}
          }
        }]
        say(
            blocks=blocks,
            text="Pick a date for me to remind you"
        )
```

</details>
