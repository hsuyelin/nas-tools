---
title: コンテキストの追加
lang: ja-jp
slug: context
order: 9
---

<div class="section-content">
すべてのリスナーは `context` ディクショナリにアクセスできます。リスナーはこれを使ってリクエストの付加情報を得ることができます。受信リクエストに含まれる `user_id`、`team_id`、`channel_id`、`enterprise_id` などの情報は、Bolt によって自動的に設定されます。

`context` は単純なディクショナリで、変更を直接加えることもできます。
</div>

```python
# ユーザーID を使って外部のシステムからタスクを取得するリスナーミドルウェア
def fetch_tasks(context, event, next):
    user = event["user"]
    try:
        # get_tasks は、ユーザー ID に対応するタスクのリストを DB から取得します
        user_tasks = db.get_tasks(user)
        tasks = user_tasks
    except Exception:
        # タスクが見つからなかった場合 get_tasks() は例外を投げます
        tasks = []
    finally:
        # ユーザーのタスクを context に設定します
        context["tasks"] = tasks
        next()

# section のブロックのリストを作成するリスナーミドルウェア
def create_sections(context, next):
    task_blocks = []
    # 先ほどのミドルウェアを使って context に追加した各タスクについて、処理を繰り返します
    for task in context["tasks"]:
        task_blocks.append(
            {
              "type": "section",
              "text": {
                  "type": "mrkdwn",
                  "text": f"*{task['title']}*
{task['body']}"
              },
              "accessory": {
                  "type": "button",
                  "text": {
                    "type": "plain_text",
                    "text":"See task"
                  },
                  "url": task["url"],
                }
            }
        )
    # ブロックのリストを context に設定します
    context["blocks"] = task_blocks
    next()

# ユーザーがアプリのホームを開くのをリッスンします
# fetch_tasks ミドルウェアを含めます
@app.event(
  event = "app_home_opened",
  middleware = [fetch_tasks, create_sections]
)
def show_tasks(event, client, context):
    # ユーザーのホームタブにビューを表示します
    client.views_publish(
        user_id=event["user"],
        view={
            "type": "home",
            "blocks": context["blocks"]
        }
    )
```
