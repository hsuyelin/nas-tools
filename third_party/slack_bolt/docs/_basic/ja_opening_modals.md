---
title: モーダルの開始
lang: ja-jp
slug: opening-modals
order: 10
---

<div class="section-content">

<a href="https://api.slack.com/block-kit/surfaces/modals">モーダル</a>は、ユーザーからのデータの入力を受け付けたり、動的な情報を表示したりするためのインターフェイスです。組み込みの APIクライアントの <a href="https://api.slack.com/methods/views.open">`views.open`</a> メソッドに、有効な `trigger_id` と<a href="https://api.slack.com/reference/block-kit/views">ビューのペイロード</a>を指定してモーダルを開始します。

ショートカットの実行、ボタンを押下、選択メニューの操作などの操作の場合、Request URL に送信されるペイロードには `trigger_id` が含まれます。

モーダルの生成方法についての詳細は、<a href="https://api.slack.com/surfaces/modals/using#composing_views">API ドキュメント</a>を参照してください。

</div>

<div>
<span class="annotation">指定可能な引数の一覧は<a href="https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html" target="_blank">モジュールドキュメント</a>を参考にしてください。</span>
```python
# ショートカットの呼び出しをリッスン
@app.shortcut("open_modal")
def open_modal(ack, body, client):
    # コマンドのリクエストを確認
    ack()
    # 組み込みのクライアントで views_open を呼び出し
    client.views_open(
        # 受け取りから 3 秒以内に有効な trigger_id を渡す
        trigger_id=body["trigger_id"],
        # ビューのペイロード
        view={
            "type": "modal",
            # ビューの識別子
            "callback_id": "view_1",
            "title": {"type": "plain_text", "text":"My App"},
            "submit": {"type": "plain_text", "text":"Submit"},
            "blocks": [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text":"Welcome to a modal with _blocks_"},
                    "accessory": {
                        "type": "button",
                        "text": {"type": "plain_text", "text":"Click me!"},
                        "action_id": "button_abc"
                    }
                },
                {
                    "type": "input",
                    "block_id": "input_c",
                    "label": {"type": "plain_text", "text":"What are your hopes and dreams?"},
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "dreamy_input",
                        "multiline":True
                    }
                }
            ]
        }
    )
```
</div>