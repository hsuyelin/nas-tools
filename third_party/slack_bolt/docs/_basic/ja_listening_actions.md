---
title: アクションのリスニング
lang: ja-jp
slug: action-listening
order: 5
---

<div class="section-content">
Bolt アプリは `action` メソッドを用いて、ボタンのクリック、メニューの選択、メッセージショートカットなどのユーザーのアクションをリッスンすることができます。

アクションは `str` 型または `re.Pattern` 型の `action_id` でフィルタリングできます。`action_id` は、Slack プラットフォーム上のインタラクティブコンポーネントを区別する一意の識別子として機能します。

`action()` を使ったすべての例で `ack()` が使用されていることに注目してください。アクションのリスナー内では、Slack からのリクエストを受信したことを確認するために、`ack()` 関数を呼び出す必要があります。これについては、[リクエストの確認](#acknowledge)セクションで説明しています。

</div>

<div>
<span class="annotation">指定可能な引数の一覧は<a href="https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html" target="_blank">モジュールドキュメント</a>を参考にしてください。</span>
```python
# 'approve_button' という action_id のブロックエレメントがトリガーされるたびに、このリスナーが呼び出させれる
@app.action("approve_button")
def update_message(ack):
    ack()
    # アクションへの反応としてメッセージを更新
```
</div>

<details class="secondary-wrapper">
<summary class="section-head" markdown="0">
<h4 class="section-head">制約付きオブジェクトを使用したアクションのリスニング</h4>
</summary>

<div class="secondary-content" markdown="0">

制約付きのオブジェクトを使用すると、`callback_id`、`block_id`、および `action_id` をそれぞれ、または任意に組み合わせてリッスンできます。オブジェクト内の制約は、`str` 型または `re.Pattern` 型で指定できます。

</div>

```python
# この関数は、block_id が 'assign_ticket' に一致し
# かつ action_id が 'select_user' に一致する場合にのみ呼び出される
@app.action({
    "block_id": "assign_ticket",
    "action_id": "select_user"
})
def update_message(ack, body, client):
    ack()

    if "container" in body and "message_ts" in body["container"]:
        client.reactions_add(
            name="white_check_mark",
            channel=body["channel"]["id"],
            timestamp=body["container"]["message_ts"],
        )
```

</details>
