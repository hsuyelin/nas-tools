---
title: アクションへの応答
lang: ja-jp
slug: action-respond
order: 6
---

<div class="section-content">

アクションへの応答には、主に 2 つの方法があります。1 つ目の最も一般的なやり方は `say()` を使用する方法です。そのリクエストが発生した会話（チャンネルや DM）にメッセージを返します。

2 つ目は、`respond()` を使用する方法です。これは、アクションに関連づけられた `response_url` を使ったメッセージ送信を行うためのユーティリティです。
</div>

<div>
<span class="annotation">指定可能な引数の一覧は<a href="https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html" target="_blank">モジュールドキュメント</a>を参考にしてください。</span>
```python
# 'approve_button' という action_id のインタラクティブコンポーネントがトリガーされると、このリスナーが呼ばれる
@app.action("approve_button")
def approve_request(ack, say):
    # アクションのリクエストを確認
    ack()
    say("Request approved 👍")
```
</div>

<details class="secondary-wrapper">
<summary class="section-head" markdown="0">
<h4 class="section-head">respond() の利用</h4>
</summary>

<div class="secondary-content" markdown="0">

`respond()` は `response_url` を使って送信するときに便利なメソッドで、これらと同じような動作をします。投稿するメッセージのペイロードには、全ての[メッセージペイロードのプロパティ](https://api.slack.com/reference/messaging/payload)とオプションのプロパティとして `response_type`（値は `"in_channel"` または `"ephemeral"`）、`replace_original`、`delete_original`、`unfurl_links`、`unfurl_media` などを指定できます。こうすることによってアプリから送信されるメッセージは、やり取りの発生元に反映されます。

</div>

```python
# 'user_select' という action_id を持つアクションのトリガーをリッスン
@app.action("user_select")
def select_user(ack, action, respond):
    ack()
    respond(f"You selected <@{action['selected_user']}>")
```

</details>
