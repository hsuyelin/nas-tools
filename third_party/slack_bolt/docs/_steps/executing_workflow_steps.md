---
title: Executing workflow steps
lang: en
slug: executing-steps
order: 5
---

<div class="section-content">

When your workflow step is executed by an end user, your app will receive a [`workflow_step_execute` event](https://api.slack.com/events/workflow_step_execute). The `execute` callback in your `WorkflowStep` configuration will be run when this event is received.

Using the `inputs` from the `save` callback, this is where you can make third-party API calls, save information to a database, update the user's Home tab, or decide the outputs that will be available to subsequent workflow steps by mapping values to the `outputs` object.

Within the `execute` callback, your app must either call `complete()` to indicate that the step's execution was successful, or `fail()` to indicate that the step's execution failed.

</div>

<div>
<span class="annotation">Refer to the module documents (<a href="https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html" target="_blank">common</a> / <a href="https://slack.dev/bolt-python/api-docs/slack_bolt/workflows/step/utilities/index.html" target="_blank">step-specific</a>) to learn the available arguments.</span>
```python
def execute(step, complete, fail):
    inputs = step["inputs"]
    # if everything was successful
    outputs = {
        "task_name": inputs["task_name"]["value"],
        "task_description": inputs["task_description"]["value"],
    }
    complete(outputs=outputs)

    # if something went wrong
    error = {"message": "Just testing step failure!"}
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