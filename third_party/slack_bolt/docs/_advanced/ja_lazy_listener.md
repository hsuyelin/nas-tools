---
title: Lazy リスナー（FaaS）
lang: ja-jp
slug: lazy-listeners
order: 10
---

<div class="section-content">
Lazy リスナー関数は、FaaS 環境への Slack アプリのデプロイを容易にする機能です。この機能は Bolt for Python でのみ利用可能で、他の Bolt フレームワークでこの機能に対応することは予定していません。

通常、アクション（action）、コマンド（command）、ショートカット（shortcut）、オプション（options）、およびモーダルからのデータ送信（view_submission）をハンドルするとき、 `ack()` を呼び出し、Slack からのリクエストを 3 秒以内に確認する必要があります。`ack()` を呼び出すと Slack に HTTP ステータスが 200 OK の応答が返されます。こうすることで、アプリがリクエストの応答を処理中であることを Slack に伝えられます。通常であれば、この確認処理を処理関数の最初のステップとして行うことを推奨しています。

しかし、FaaS 環境や類似のランタイムで実行されるアプリでは、 **HTTP レスポンスを返したあとにスレッドやプロセスの実行を続けることができない** ため、確認の応答を送信した後で時間のかかる処理をするという通常のパターンに従うことができません。こうした環境で動作させるためには、 `process_before_response` フラグを `True` に設定します。このフラグが `True` に設定されている場合、Bolt はリスナー関数での処理が完了するまで HTTP レスポンスの送信を遅延させます。そのため 3 秒以内にリスナーのすべての処理が完了しなかった場合は Slack 上でタイムアウトのエラー表示となってしまいます。また、Events API に応答するリスナーでは明示的な `ack()` メソッドの呼び出しを必要としませんが、この設定を有効にしている場合、リスナーの処理を 3 秒以内に完了させる必要があることにも注意してください。

処理関数の中で時間のかかる処理を実行できるようにするために、私たちは Lazy リスナーという関数を実行する仕組みを導入しました。Lazy リスナーは、デコレーターとして動作させるのではなく、以下の 2 つのキーワード引数を受け取ります。
* `ack: Callable`: 3 秒以内での `ack()` メソッドの呼び出しを担当します。 
* `lazy: List[Callable]` : リクエストに関する時間のかかる処理のハンドリングを担当します。Lazy 関数からは `ack()` にアクセスすることはできません。
</div>

```python
def respond_to_slack_within_3_seconds(body, ack):
    text = body.get("text")
    if text is None or len(text) == 0:
        ack(f":x:Usage: /start-process (description here)")
    else:
        ack(f"Accepted! (task: {body['text']})")

import time
def run_long_process(respond, body):
    time.sleep(5)  # 3 秒より長い時間を指定します
    respond(f"Completed! (task: {body['text']})")

app.command("/start-process")(
    # この場合でも ack() は 3 秒以内に呼ばれます
    ack=respond_to_slack_within_3_seconds,
    # Lazy 関数がイベントの処理を担当します
    lazy=[run_long_process]
)
```

<details class="secondary-wrapper">
<summary class="section-head" markdown="0">
<h4 class="section-head">AWS Lambda を使用した例</h4>
</summary>

<div class="secondary-content" markdown="0">
このサンプルは、[AWS Lambda](https://aws.amazon.com/lambda/) にコードをデプロイします。[`examples` フォルダ](https://github.com/slackapi/bolt-python/tree/main/examples/aws_lambda)にはほかにもサンプルが用意されています。

```bash
pip install slack_bolt
# ソースコードを main.py として保存します
# config.yaml を設定してハンドラーを `handler: main.handler` で参照できるようにします

# https://pypi.org/project/python-lambda/
pip install python-lambda

# config.yml を適切に設定します
# lazy リスナーの実行には lambda:InvokeFunction と lambda:GetFunction が必要です
export SLACK_SIGNING_SECRET=***
export SLACK_BOT_TOKEN=xoxb-***
echo 'slack_bolt' > requirements.txt
lambda deploy --config-file config.yaml --requirements requirements.txt
```
</div>

```python
from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler

# FaaS で実行するときは process_before_response を True にする必要があります
app = App(process_before_response=True)

def respond_to_slack_within_3_seconds(body, ack):
    text = body.get("text")
    if text is None or len(text) == 0:
        ack(":x: Usage: /start-process (description here)")
    else:
        ack(f"Accepted! (task: {body['text']})")

import time
def run_long_process(respond, body):
    time.sleep(5)  # 3 秒より長い時間を指定します
    respond(f"Completed! (task: {body['text']})")

app.command("/start-process")(
    ack=respond_to_slack_within_3_seconds,  # `ack()` の呼び出しを担当します
    lazy=[run_long_process]  # `ack()` の呼び出しはできません。複数の関数を持たせることができます。
)

def handler(event, context):
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)
```

このサンプルアプリを実行するには、以下の IAM 権限が必要になります。

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "lambda:InvokeFunction",
                "lambda:GetFunction"
            ],
            "Resource": "*"
        }
    ]
}
```
</details>
