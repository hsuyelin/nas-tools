---
title: ステップの追加・編集
lang: ja-jp
slug: adding-editing-steps
order: 3
---

<div class='section-content'>

作成したワークフローステップがワークフローに追加またはその設定を変更されるタイミングで、[`workflow_step_edit` イベントがアプリに送信されます](https://api.slack.com/reference/workflows/workflow_step_edit)。このイベントがアプリに届くと、`WorkflowStep` で設定した `edit` コールバックが実行されます。

ステップの追加と編集のどちらが行われるときも、[ワークフローステップの設定モーダル](https://api.slack.com/reference/workflows/configuration-view)をビルダーに送信する必要があります。このモーダルは、そのステップ独自の設定を選択するための場所です。通常のモーダルより制限が強く、例えば `title`、`submit`、`close` のプロパティを含めることができません。設定モーダルの `callback_id` は、デフォルトではワークフローステップと同じものになります。

`edit` コールバック内で `configure()` ユーティリティを使用すると、対応する `blocks` 引数にビューのblocks 部分だけを渡して、ステップの設定モーダルを簡単に表示させることができます。必要な入力内容が揃うまで設定の保存を無効にするには、`True` の値をセットした `submit_disabled` を渡します。

設定モーダルの開き方に関する詳細は、[こちらのドキュメント](https://api.slack.com/workflows/steps#handle_config_view)を参照してください。

</div>

<div>
<span class="annotation">指定可能な引数の一覧はモジュールドキュメントを参考にしてください（<a href="https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html" target="_blank">共通</a> / <a href="https://slack.dev/bolt-python/api-docs/slack_bolt/workflows/step/utilities/index.html" target="_blank">ステップ用</a>）</span>
```python
def edit(ack, step, configure):
    ack()

    blocks = [
        {
            "type": "input",
            "block_id": "task_name_input",
            "element": {
                "type": "plain_text_input",
                "action_id": "name",
                "placeholder": {"type": "plain_text", "text":"Add a task name"},
            },
            "label": {"type": "plain_text", "text":"Task name"},
        },
        {
            "type": "input",
            "block_id": "task_description_input",
            "element": {
                "type": "plain_text_input",
                "action_id": "description",
                "placeholder": {"type": "plain_text", "text":"Add a task description"},
            },
            "label": {"type": "plain_text", "text":"Task description"},
        },
    ]
    configure(blocks=blocks)

ws = WorkflowStep(
    callback_id="add_task",
    edit=edit,
    save=save,
    execute=execute,
)
app.step(ws)
```
</div>