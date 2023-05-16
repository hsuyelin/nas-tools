---
title: コマンドのリスニングと応答
lang: ja-jp
slug: commands
order: 9
---

<div class="section-content">

スラッシュコマンドが実行されたリクエストをリッスンするには、`command()` メソッドを使用します。このメソッドでは `str` 型の `command_name` の指定が必要です。

コマンドリクエストをアプリが受信し確認したことを Slack に通知するため、`ack()` を呼び出す必要があります。

スラッシュコマンドに応答する方法は 2 つあります。1 つ目は `say()` を使う方法で、文字列または JSON のペイロードを渡すことができます。2 つ目は `respond()` を使う方法です。これは `response_url` がある場合に活躍します。これらの方法は[アクションへの応答](#action-respond)セクションで詳しく説明しています。

アプリの設定でコマンドを登録するときは、リクエスト URL の末尾に `/slack/events` をつけます。

</div>

<div>
<span class="annotation">指定可能な引数の一覧は<a href="https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html" target="_blank">モジュールドキュメント</a>を参考にしてください。</span>
```python
# echoコマンドは受け取ったコマンドをそのまま返す
@app.command("/echo")
def repeat_text(ack, respond, command):
    # command リクエストを確認
    ack()
    respond(f"{command['text']}")
```
</div>
