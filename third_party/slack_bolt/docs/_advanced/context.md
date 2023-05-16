---
title: Adding context
lang: en
slug: context
order: 9
---

<div class="section-content">
All listeners have access to a `context` dictionary, which can be used to enrich requests with additional information. Bolt automatically attaches information that is included in the incoming request, like `user_id`, `team_id`, `channel_id`, and `enterprise_id`.

`context` is just a dictionary, so you can directly modify it.
</div>

```python
# Listener middleware to fetch tasks from external system using user ID
def fetch_tasks(context, event, next):
    user = event["user"]
    try:
        # Assume get_tasks fetchs list of tasks from DB corresponding to user ID
        user_tasks = db.get_tasks(user)
        tasks = user_tasks
    except Exception:
        # get_tasks() raises exception because no tasks are found
        tasks = []
    finally:
        # Put user's tasks in context
        context["tasks"] = tasks
        next()

# Listener middleware to create a list of section blocks
def create_sections(context, next):
    task_blocks = []
    # Loops through tasks added to context in previous middleware
    for task in context["tasks"]:
        task_blocks.append(
            {
              "type": "section",
              "text": {
                  "type": "mrkdwn",
                  "text": f"*{task['title']}*\n{task['body']}"
              },
              "accessory": {
                  "type": "button",
                  "text": {
                    "type": "plain_text",
                    "text": "See task"
                  },
                  "url": task["url"],
                }
            }
        )
    # Put list of blocks in context
    context["blocks"] = task_blocks
    next()

# Listen for user opening app home
# Include fetch_tasks middleware
@app.event(
  event = "app_home_opened",
  middleware = [fetch_tasks, create_sections]
)
def show_tasks(event, client, context):
    # Publish view to user's home tab
    client.views_publish(
        user_id=event["user"],
        view={
            "type": "home",
            "blocks": context["blocks"]
        }
    )
```
