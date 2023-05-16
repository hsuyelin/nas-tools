from slack_sdk.web.async_client import AsyncWebClient


class AsyncComplete:
    """`complete()` utility to tell Slack the completion of a workflow step execution.

        async def execute(step, complete, fail):
            inputs = step["inputs"]
            # if everything was successful
            outputs = {
                "task_name": inputs["task_name"]["value"],
                "task_description": inputs["task_description"]["value"],
            }
            await complete(outputs=outputs)

        ws = AsyncWorkflowStep(
            callback_id="add_task",
            edit=edit,
            save=save,
            execute=execute,
        )
        app.step(ws)

    This utility is a thin wrapper of workflows.stepCompleted API method.
    Refer to https://api.slack.com/methods/workflows.stepCompleted for details.
    """

    def __init__(self, *, client: AsyncWebClient, body: dict):
        self.client = client
        self.body = body

    async def __call__(self, **kwargs) -> None:
        await self.client.workflows_stepCompleted(
            workflow_step_execute_id=self.body["event"]["workflow_step"]["workflow_step_execute_id"],
            **kwargs,
        )
