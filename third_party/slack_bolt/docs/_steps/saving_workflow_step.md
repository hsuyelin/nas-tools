---
title: Saving step configurations
lang: en
slug: saving-steps
order: 4
---

<div class='section-content'>

After the configuration modal is opened, your app will listen for the `view_submission` event. The `save` callback in your `WorkflowStep` configuration will be run when this event is received.

Within the `save` callback, the `update()` method can be used to save the builder's step configuration by passing in the following arguments:

- `inputs` is a dictionary representing the data your app expects to receive from the user upon workflow step execution.
- `outputs` is a list of objects containing data that your app will provide upon the workflow step's completion. Outputs can then be used in subsequent steps of the workflow.
- `step_name` overrides the default Step name
- `step_image_url` overrides the default Step image

To learn more about how to structure these parameters, [read the documentation](https://api.slack.com/reference/workflows/workflow_step).

</div>

<div>
<span class="annotation">Refer to the module documents (<a href="https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html" target="_blank">common</a> / <a href="https://slack.dev/bolt-python/api-docs/slack_bolt/workflows/step/utilities/index.html" target="_blank">step-specific</a>) to learn the available arguments.</span>
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
```
</div>