from typing import Optional, Union, Sequence

from slack_sdk.web import WebClient
from slack_sdk.models.blocks import Block


class Configure:
    """`configure()` utility to send the modal view in Workflow Builder.

        def edit(ack, step, configure):
            ack()

            blocks = [
                {
                    "type": "input",
                    "block_id": "task_name_input",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "name",
                        "placeholder": {"type": "plain_text", "text": "Add a task name"},
                    },
                    "label": {"type": "plain_text", "text": "Task name"},
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

    Refer to https://api.slack.com/workflows/steps for details.
    """

    def __init__(self, *, callback_id: str, client: WebClient, body: dict):
        self.callback_id = callback_id
        self.client = client
        self.body = body

    def __call__(self, *, blocks: Optional[Sequence[Union[dict, Block]]] = None, **kwargs) -> None:
        self.client.views_open(
            trigger_id=self.body["trigger_id"],
            view={
                "type": "workflow_step",
                "callback_id": self.callback_id,
                "blocks": blocks,
                **kwargs,
            },
        )
