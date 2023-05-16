---
title: ショートカットのリスニングと応答
lang: ja-jp
slug: shortcuts
order: 8
---

<div class="section-content">

`shortcut()` メソッドは、[グローバルショートカット](https://api.slack.com/interactivity/shortcuts/using#global_shortcuts)と[メッセージショートカット](https://api.slack.com/interactivity/shortcuts/using#message_shortcuts)の 2 つをサポートしています。

ショートカットは、いつでも呼び出せるアプリのエントリーポイントを提供するものです。グローバルショートカットは Slack のテキスト入力エリアや検索ウィンドウからアクセスできます。メッセージショートカットはメッセージのコンテキストメニューからアクセスできます。アプリは、ショートカットリクエストをリッスンするために `shortcut()` メソッドを使用します。このメソッドには `str` 型または `re.Pattern` 型の `callback_id` パラメーターを指定します。

ショートカットリクエストがアプリによって確認されたことを Slack に伝えるため、`ack()` を呼び出す必要があります。

ショートカットのペイロードには `trigger_id` が含まれます。アプリはこれを使って、ユーザーにやろうとしていることを確認するための[モーダルを開く](#creating-modals)ことができます。

アプリの設定でショートカットを登録する際は、他の URL と同じように、リクエスト URL の末尾に `/slack/events` をつけます。

⚠️ グローバルショートカットのペイロードにはチャンネル ID が **含まれません**。アプリでチャンネル ID を取得する必要がある場合は、モーダル内に [`conversations_select`](https://api.slack.com/reference/block-kit/block-elements#conversation_select) エレメントを配置します。メッセージショートカットにはチャンネル ID が含まれます。

</div>

<div>
<span class="annotation">指定可能な引数の一覧は<a href="https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html" target="_blank">モジュールドキュメント</a>を参考にしてください。</span>
```python
# 'open_modal' という callback_id のショートカットをリッスン
@app.shortcut("open_modal")
def open_modal(ack, shortcut, client):
    # ショートカットのリクエストを確認
    ack()
    # 組み込みのクライアントを使って views_open メソッドを呼び出す
    client.views_open(
        trigger_id=shortcut["trigger_id"],
        # モーダルで表示するシンプルなビューのペイロード
        view={
            "type": "modal",
            "title": {"type": "plain_text", "text":"My App"},
            "close": {"type": "plain_text", "text":"Close"},
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text":"About the simplest modal you could conceive of :smile:\n\nMaybe <https://api.slack.com/reference/block-kit/interactive-components|*make the modal interactive*> or <https://api.slack.com/surfaces/modals/using#modifying|*learn more advanced modal use cases*>."
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text":"Psssst this modal was designed using <https://api.slack.com/tools/block-kit-builder|*Block Kit Builder*>"
                        }
                    ]
                }
            ]
        }
    )
```
</div>

<details class="secondary-wrapper">
<summary class="section-head" markdown="0">
<h4 class="section-head">制約付きオブジェクトを使用したショートカットのリスニング</h4>
</summary>

<div class="secondary-content" markdown="0">
制約付きオブジェクトを使って `callback_id` や `type` によるリッスンできます。オブジェクト内の制約は `str` 型または `re.Pattern` オブジェクトを使用できます。
</div>

```python

# このリスナーが呼び出されるのは、callback_id が 'open_modal' と一致し
# かつ type が 'message_action' と一致するときのみ
@app.shortcut({"callback_id": "open_modal", "type": "message_action"})
def open_modal(ack, shortcut, client):
    # ショートカットのリクエストを確認
    ack()
    # 組み込みのクライアントを使って views_open メソッドを呼び出す
    client.views_open(
        trigger_id=shortcut["trigger_id"],
        view={
            "type": "modal",
            "title": {"type": "plain_text", "text":"My App"},
            "close": {"type": "plain_text", "text":"Close"},
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text":"About the simplest modal you could conceive of :smile:\n\nMaybe <https://api.slack.com/reference/block-kit/interactive-components|*make the modal interactive*> or <https://api.slack.com/surfaces/modals/using#modifying|*learn more advanced modal use cases*>."
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text":"Psssst this modal was designed using <https://api.slack.com/tools/block-kit-builder|*Block Kit Builder*>"
                        }
                    ]
                }
            ]
        }
    )
```

</details>
