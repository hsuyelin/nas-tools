---
title: Publishing views to App Home
lang: en
slug: app-home
order: 13
---

<div class="section-content">
<a href="https://api.slack.com/surfaces/tabs/using">Home tabs</a> are customizable surfaces accessible via the sidebar and search that allow apps to display views on a per-user basis. After enabling App Home within your app configuration, home tabs can be published and updated by passing a `user_id` and <a href="https://api.slack.com/reference/block-kit/views">view payload</a> to the <a href="https://api.slack.com/methods/views.publish">`views.publish`</a> method.

You can subscribe to the <a href="https://api.slack.com/events/app_home_opened">`app_home_opened`</a> event to listen for when users open your App Home.
</div>

<div>
<span class="annotation">Refer to <a href="https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html" target="_blank">the module document</a> to learn the available listener arguments.</span>
```python
@app.event("app_home_opened")
def update_home_tab(client, event, logger):
    try:
        # Call views.publish with the built-in client
        client.views_publish(
            # Use the user ID associated with the event
            user_id=event["user"],
            # Home tabs must be enabled in your app configuration
            view={
                "type": "home",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Welcome home, <@" + event["user"] + "> :house:*"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                          "type": "mrkdwn",
                          "text": "Learn how home tabs can be more useful and interactive <https://api.slack.com/surfaces/tabs/using|*in the documentation*>."
                        }
                    }
                ]
            }
        )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")
```
</div>