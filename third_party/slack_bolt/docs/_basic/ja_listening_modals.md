---
title: モーダルの送信のリスニング
lang: ja-jp
slug: view_submissions
order: 12
---

<div class="section-content">

<a href="https://api.slack.com/reference/block-kit/views">モーダルのペイロード</a>に `input` ブロックを含める場合、その入力値を受け取るために`view_submission` リクエストをリッスンする必要があります。`view_submission` リクエストのリッスンには、組み込みの`view()` メソッドを利用することができます。`view()` の引数には、`str` 型または `re.Pattern` 型の `callback_id` を指定します。

`input` ブロックの値にアクセスするには `state` オブジェクトを参照します。`state` 内には `values` というオブジェクトがあり、`block_id` と一意の `action_id` に紐づける形で入力値を保持しています。

---

##### モーダル送信でのビューの更新

`view_submission` リクエストに対してモーダルを更新するには、リクエストの確認の中で `update` という `response_action` と新しく作成した `view` を指定します。

```python
# モーダル送信でのビューの更新
@app.view("view_1")
def handle_submission(ack, body):
    ack(response_action="update", view=build_new_view(body))
```
この例と同様に、モーダルでの送信リクエストに対して、<a href="https://api.slack.com/surfaces/modals/using#displaying_errors">エラーを表示する</a>ためのオプションもあります。

モーダルの送信について詳しくは、<a href="https://api.slack.com/surfaces/modals/using#handling_submissions">API ドキュメント</a>を参照してください。

---

##### モーダルが閉じられたときの対応

`view_closed` リクエストをリッスンするためには `callback_id` を指定して、かつ `notify_on_close` 属性をモーダルのビューに設定する必要があります。以下のコード例をご覧ください。

よく詳しい情報は、<a href="https://api.slack.com/surfaces/modals/using#modal_cancellations">API ドキュメント</a>を参照してください。

```python
client.views_open(
    trigger_id=body.get("trigger_id"),
    view={
        "type": "modal",
        "callback_id": "modal-id",  # view_closed の処理時に必要
        "title": {
            "type": "plain_text",
            "text": "Modal title"
        },
        "blocks": [],
        "close": {
            "type": "plain_text",
            "text": "Cancel"
        },
        "notify_on_close": True,  # この属性は必須
    }
)
# view_closed リクエストを処理する
@app.view_closed("modal-id")
def handle_view_closed(ack, body, logger):
    ack()
    logger.info(body)
```

</div>

<div>
<span class="annotation">指定可能な引数の一覧は<a href="https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html" target="_blank">モジュールドキュメント</a>を参考にしてください。</span>
```python
# view_submission リクエストを処理
@app.view("view_1")
def handle_submission(ack, body, client, view, logger):
    # `input_c`という block_id に `dreamy_input` を持つ input ブロックがある場合
    hopes_and_dreams = view["state"]["values"]["input_c"]["dreamy_input"]
    user = body["user"]["id"]
    # 入力値を検証
    errors = {}
    if hopes_and_dreams is not None and len(hopes_and_dreams) <= 5:
        errors["input_c"] = "The value must be longer than 5 characters"
    if len(errors) > 0:
        ack(response_action="errors", errors=errors)
        return
    # view_submission リクエストの確認を行い、モーダルを閉じる
    ack()
    # 入力されたデータを使った処理を実行。このサンプルでは DB に保存する処理を行う
    # そして入力値の検証結果をユーザーに送信

    # ユーザーに送信するメッセージ
    msg = ""
    try:
        # DB に保存
        msg = f"Your submission of {hopes_and_dreams} was successful"
    except Exception as e:
        # エラーをハンドリング
        msg = "There was an error with your submission"

    # ユーザーにメッセージを送信
    try:
        client.chat_postMessage(channel=user, text=msg)
    except e:
        logger.exception(f"Failed to post a message {e}")

```
</div>
