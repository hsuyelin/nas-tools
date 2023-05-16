---
title: ステップの実行
lang: ja-jp
slug: executing-steps
order: 5
---

<div class="section-content">

エンドユーザーがワークフローステップを実行すると、アプリに [`workflow_step_execute` イベントが送信されます](https://api.slack.com/events/workflow_step_execute)。このイベントがアプリに届くと、`WorkflowStep` で設定した `execute` コールバックが実行されます。

`save` コールバックで取り出した `inputs` を使って、サードパーティの API を呼び出す、情報をデータベースに保存する、ユーザーのホームタブを更新するといった処理を実行することができます。また、ワークフローの後続のステップで利用する出力値を `outputs` オブジェクトに設定します。

`execute` コールバック内では、`complete()` を呼び出してステップの実行が成功したことを示すか、`fail()` を呼び出してステップの実行が失敗したことを示す必要があります。

</div>

<div>
<span class="annotation">指定可能な引数の一覧はモジュールドキュメントを参考にしてください（<a href="https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html" target="_blank">共通</a> / <a href="https://slack.dev/bolt-python/api-docs/slack_bolt/workflows/step/utilities/index.html" target="_blank">ステップ用</a>）</span>
```python
def execute(step, complete, fail):
    inputs = step["inputs"]
    # すべての処理が成功した場合
    outputs = {
        "task_name": inputs["task_name"]["value"],
        "task_description": inputs["task_description"]["value"],
    }
    complete(outputs=outputs)

    # 失敗した処理がある場合
    error = {"message":"Just testing step failure!"}
    fail(error=error)

ws = WorkflowStep(
    callback_id="add_task",
    edit=edit,
    save=save,
    execute=execute,
)
app.step(ws)
```
</div>