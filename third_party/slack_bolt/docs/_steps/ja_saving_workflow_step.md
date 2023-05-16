---
title: ステップの設定の保存
lang: ja-jp
slug: saving-steps
order: 4
---

<div class='section-content'>

設定モーダルを開いた後、アプリは `view_submission` イベントをリッスンします。このイベントがアプリに届くと、`WorkflowStep` で設定した `save` コールバックが実行されます。

`save` コールバック内では、`update()` メソッドを使って、ワークフローに追加されたステップの設定を保存することができます。このメソッドには次の引数を指定します。

- `inputs` : ユーザーがワークフローステップを実行したときにアプリが受け取る予定のデータを表す辞書型の値です。
- `outputs` : ワークフローステップの完了時にアプリが出力するデータが設定されたオブジェクトのリストです。この outputs は、ワークフローの後続のステップで利用することができます。
- `step_name` : ステップのデフォルトの名前をオーバーライドします。
- `step_image_url` : ステップのデフォルトの画像をオーバーライドします。

これらのパラメータの構成方法に関する詳細は、[こちらのドキュメント](https://api.slack.com/reference/workflows/workflow_step)を参照してください。

</div>

<div>
<span class="annotation">指定可能な引数の一覧はモジュールドキュメントを参考にしてください（<a href="https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html" target="_blank">共通</a> / <a href="https://slack.dev/bolt-python/api-docs/slack_bolt/workflows/step/utilities/index.html" target="_blank">ステップ用</a>）</span>
```python
def save(ack, view, update):
    ack()

    values = view["state"]["values"]
    task_name = values["task_name_input"]["name"]
    task_description = values["task_description_input"]["description"]

    inputs = {
        "task_name": {"value": task_name["value"]},
        "task_description": {"value": task_description["value"]}
    }
    outputs = [
        {
            "type": "text",
            "name": "task_name",
            "label":"Task name",
        },
        {
            "type": "text",
            "name": "task_description",
            "label":"Task description",
        }
    ]
    update(inputs=inputs, outputs=outputs)

ws = WorkflowStep(
    callback_id="add_task",
    edit=edit,
    save=save,
    execute=execute,
)
app.step(ws)
```
</div>