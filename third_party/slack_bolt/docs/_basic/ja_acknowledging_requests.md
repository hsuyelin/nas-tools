---
title: リクエストの確認
lang: ja-jp
slug: acknowledge
order: 7
---

<div class="section-content">

アクション（action）、コマンド（command）、ショートカット（shortcut）、オプション（options）、およびモーダルからのデータ送信（view_submission）の各リクエストは、**必ず** `ack()` 関数を使って確認を行う必要があります。これによってリクエストが受信されたことが Slack に認識され、Slack のユーザーインターフェイスが適切に更新されます。

リクエストの種類によっては、確認で通知方法が異なる場合があります。例えば、外部データソースを使用する選択メニューのオプションのリクエストに対する確認では、適切な[オプション](https://api.slack.com/reference/block-kit/composition-objects#option)のリストとともに `ack()` を呼び出します。モーダルからのデータ送信に対する確認では、 `response_action` を渡すことで[モーダルの更新](#update-views-on-submission)などを行えます。

確認までの猶予は 3 秒しかないため、新しいメッセージの送信やデータベースからの情報の取得といった時間のかかる処理は、`ack()` を呼び出した後で行うことをおすすめします。

 FaaS / serverless 環境を使う場合、 `ack()` するタイミングが異なります。 これに関する詳細は [Lazy listeners (FaaS)](#lazy-listeners) を参照してください。 
</div>

<div>
<span class="annotation">指定可能な引数の一覧は<a href="https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html" target="_blank">モジュールドキュメント</a>を参考にしてください。</span>
```python
# 外部データを使用する選択メニューオプションに応答するサンプル
@app.options("menu_selection")
def show_menu_options(ack):
    options = [
        {
            "text": {"type": "plain_text", "text":"Option 1"},
            "value":"1-1",
        },
        {
            "text": {"type": "plain_text", "text":"Option 2"},
            "value":"1-2",
        },
    ]
    ack(options=options)
```
</div>