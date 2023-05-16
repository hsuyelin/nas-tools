from slack_sdk.web import WebClient


class Update:
    """`update()` utility to tell Slack the processing results of a `save` listener.

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
                    "label": "Task name",
                },
                {
                    "type": "text",
                    "name": "task_description",
                    "label": "Task description",
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

    This utility is a thin wrapper of workflows.stepFailed API method.
    Refer to https://api.slack.com/methods/workflows.updateStep for details.
    """

    def __init__(self, *, client: WebClient, body: dict):
        self.client = client
        self.body = body

    def __call__(self, **kwargs) -> None:
        self.client.workflows_updateStep(
            workflow_step_edit_id=self.body["workflow_step"]["workflow_step_edit_id"],
            **kwargs,
        )
