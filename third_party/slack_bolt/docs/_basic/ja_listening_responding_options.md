---
title: オプションのリスニングと応答
lang: ja-jp
slug: options
order: 14
---

<div class="section-content">
`options()` メソッドは、Slack からのオプション（セレクトメニュー内の動的な選択肢）をリクエストするペイロードをリッスンします。 [`action()` と同様に](#action-listening)、文字列型の `action_id` または制約付きオブジェクトが必要です。

外部データソースを使って選択メニューをロードするためには、末部に `/slack/events` が付加された URL を Options Load URL として予め設定しておく必要があります。

`external_select` メニューでは `action_id` を指定することをおすすめしています。ただし、ダイアログを利用している場合、ダイアログが Block Kit に対応していないため、`callback_id` をフィルタリングするための制約オブジェクトを使用する必要があります。

オプションのリクエストに応答するときは、有効なオプションを含む `options` または `option_groups` のリストとともに `ack()` を呼び出す必要があります。API サイトにある[外部データを使用する選択メニューに応答するサンプル例](https://api.slack.com/reference/messaging/block-elements#external-select)と、[ダイアログでの応答例](https://api.slack.com/dialogs#dynamic_select_elements_external)を参考にしてください。

さらに、ユーザーが入力したキーワードに基づいたオプションを返すようフィルタリングロジックを適用することもできます。 これは `payload` という引数の ` value` の値に基づいて、それぞれのパターンで異なるオプションの一覧を返すように実装することができます。 Bolt for Python のすべてのリスナーやミドルウェアでは、[多くの有用な引数](https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html)にアクセスすることができますので、チェックしてみてください。

</div>

<div>
<span class="annotation">指定可能な引数の一覧は<a href="https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html" target="_blank">モジュールドキュメント</a>を参考にしてください。</span>
```python
# 外部データを使用する選択メニューオプションに応答するサンプル例
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
