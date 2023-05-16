---
title: アダプター
lang: ja-jp
slug: adapters
order: 0
---

<div class="section-content">
アダプターは Slack から届く受信リクエストの受付とパーズを担当し、それらのリクエストを <a href="https://github.com/slackapi/bolt-python/blob/main/slack_bolt/request/request.py">`BoltRequest`</a> の形式に変換して Bolt アプリに引き渡します。

デフォルトでは、Bolt の組み込みの <a href="https://docs.python.org/3/library/http.server.html">`HTTPServer`</a> アダプターが使われます。このアダプターは、ローカルで開発するのには問題がありませんが、<b>本番環境での利用は推奨されていません</b>。Bolt for Python には複数の組み込みのアダプターが用意されており、必要に応じてインポートしてアプリで使用することができます。組み込みのアダプターは Flask、Django、Starlette をはじめとする様々な人気の Python フレームワークをサポートしています。これらのアダプターは、あなたが選択した本番環境で利用可能な Webサーバーとともに利用することができます。

アダプターを使用するには、任意のフレームワークを使ってアプリを開発し、そのコードに対応するアダプターをインポートします。その後、アダプターのインスタンスを初期化して、受信リクエストの受付とパーズを行う関数を呼び出します。

すべてのアダプターの一覧と、設定や使い方のサンプルは、リポジトリの <a href="https://github.com/slackapi/bolt-python/tree/main/examples">`examples` フォルダ</a>をご覧ください。
</div>

```python
from slack_bolt import App
app = App(
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    token=os.environ.get("SLACK_BOT_TOKEN")
)

# ここには Flask 固有の記述はありません
# App はフレームワークやランタイムに一切依存しません
@app.command("/hello-bolt")
def hello(body, ack):
    ack(f"Hi <@{body['user_id']}>!")

# Flask アプリを初期化します
from flask import Flask, request
flask_app = Flask(__name__)

# SlackRequestHandler は WSGI のリクエストを Bolt のインターフェイスに合った形に変換します
# Bolt レスポンスからの WSGI レスポンスの作成も行います
from slack_bolt.adapter.flask import SlackRequestHandler
handler = SlackRequestHandler(app)

# Flask アプリへのルートを登録します
@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    # handler はアプリのディスパッチメソッドを実行します
    return handler.handle(request)
```
