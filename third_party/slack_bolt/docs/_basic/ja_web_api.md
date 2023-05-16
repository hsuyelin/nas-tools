---
title: Web API の使い方
lang: ja-jp
slug: web-api
order: 4
---

<div class="section-content">
`app.client`、またはミドルウェア・リスナーの引数 `client` として Bolt アプリに提供されている [`WebClient`](https://slack.dev/python-slack-sdk/basic_usage.html) は必要な権限を付与されており、これを利用することで[あらゆる Web API メソッド](https://api.slack.com/methods)を呼び出すことができます。このクライアントのメソッドを呼び出すと `SlackResponse` という Slack からの応答情報を含むオブジェクトが返されます。

Bolt の初期化に使用するトークンは `context` オブジェクトに設定されます。このトークンは、多くの Web API メソッドを呼び出す際に必要となります。

</div>

<div>
<span class="annotation">指定可能な引数の一覧は<a href="https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html" target="_blank">モジュールドキュメント</a>を参考にしてください。</span>
```python
@app.message("wake me up")
def say_hello(client, message):
    # 2020 年 9 月 30 日午後 11:59:59 を示す Unix エポック秒
    when_september_ends = 1601510399
    channel_id = message["channel"]
    client.chat_scheduleMessage(
        channel=channel_id,
        post_at=when_september_ends,
        text="Summer has come and passed"
    )
```
</div>