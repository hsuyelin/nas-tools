from slack_sdk.web.async_client import AsyncWebClient


class AsyncFail:
    """`fail()` utility to tell Slack the execution failure of a workflow step.

        async def execute(step, complete, fail):
            inputs = step["inputs"]
            # if something went wrong
            error = {"message": "Just testing step failure!"}
            await fail(error=error)

        ws = AsyncWorkflowStep(
            callback_id="add_task",
            edit=edit,
            save=save,
            execute=execute,
        )
        app.step(ws)

    This utility is a thin wrapper of workflows.stepFailed API method.
    Refer to https://api.slack.com/methods/workflows.stepFailed for details.
    """

    def __init__(self, *, client: AsyncWebClient, body: dict):
        self.client = client
        self.body = body

    async def __call__(
        self,
        *,
        error: dict,
    ) -> None:
        await self.client.workflows_stepFailed(
            workflow_step_execute_id=self.body["event"]["workflow_step"]["workflow_step_execute_id"],
            error=error,
        )
