import logging

from slack_sdk import WebClient
from slack_sdk.web import SlackResponse

from slack_bolt import App, Ack

logging.basicConfig(level=logging.DEBUG)

# export SLACK_SIGNING_SECRET=***
# export SLACK_BOT_TOKEN=xoxb-***
app = App()


# https://api.slack.com/tutorials/workflow-builder-steps


@app.action({"type": "workflow_step_edit", "callback_id": "copy_review"})
def edit(body: dict, ack: Ack, client: WebClient):
    ack()
    new_modal: SlackResponse = client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "workflow_step",
            "callback_id": "copy_review_view",
            "blocks": [
                {
                    "type": "section",
                    "block_id": "intro-section",
                    "text": {
                        "type": "plain_text",
                        "text": "Create a task in one of the listed projects. The link to the task and other details will be available as variable data in later steps.",  # noqa: E501
                    },
                },
                {
                    "type": "input",
                    "block_id": "task_name_input",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "task_name",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Write a task name",
                        },
                    },
                    "label": {"type": "plain_text", "text": "Task name"},
                },
                {
                    "type": "input",
                    "block_id": "task_description_input",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "task_description",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Write a description for your task",
                        },
                    },
                    "label": {"type": "plain_text", "text": "Task description"},
                },
                {
                    "type": "input",
                    "block_id": "task_author_input",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "task_author",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Write a task name",
                        },
                    },
                    "label": {"type": "plain_text", "text": "Task author"},
                },
            ],
        },
    )


@app.view("copy_review_view")
def save(ack: Ack, client: WebClient, body: dict):
    state_values = body["view"]["state"]["values"]
    response: SlackResponse = client.api_call(
        api_method="workflows.updateStep",
        json={
            "workflow_step_edit_id": body["workflow_step"]["workflow_step_edit_id"],
            "inputs": {
                "taskName": {
                    "value": state_values["task_name_input"]["task_name"]["value"],
                },
                "taskDescription": {
                    "value": state_values["task_description_input"]["task_description"]["value"],
                },
                "taskAuthorEmail": {
                    "value": state_values["task_author_input"]["task_author"]["value"],
                },
            },
            "outputs": [
                {
                    "name": "taskName",
                    "type": "text",
                    "label": "Task Name",
                },
                {
                    "name": "taskDescription",
                    "type": "text",
                    "label": "Task Description",
                },
                {
                    "name": "taskAuthorEmail",
                    "type": "text",
                    "label": "Task Author Email",
                },
            ],
        },
    )
    ack()


pseudo_database = {}


@app.event("workflow_step_execute")
def execute(body: dict, client: WebClient):
    step = body["event"]["workflow_step"]
    completion: SlackResponse = client.api_call(
        api_method="workflows.stepCompleted",
        json={
            "workflow_step_execute_id": step["workflow_step_execute_id"],
            "outputs": {
                "taskName": step["inputs"]["taskName"]["value"],
                "taskDescription": step["inputs"]["taskDescription"]["value"],
                "taskAuthorEmail": step["inputs"]["taskAuthorEmail"]["value"],
            },
        },
    )
    user: SlackResponse = client.users_lookupByEmail(email=step["inputs"]["taskAuthorEmail"]["value"])
    user_id = user["user"]["id"]
    new_task = {
        "task_name": step["inputs"]["taskName"]["value"],
        "task_description": step["inputs"]["taskDescription"]["value"],
    }
    tasks = pseudo_database.get(user_id, [])
    tasks.append(new_task)
    pseudo_database[user_id] = tasks

    blocks = []
    for task in tasks:
        blocks.append(
            {
                "type": "section",
                "text": {"type": "plain_text", "text": task["task_name"]},
            }
        )
        blocks.append({"type": "divider"})

    home_tab_update: SlackResponse = client.views_publish(
        user_id=user_id,
        view={
            "type": "home",
            "title": {"type": "plain_text", "text": "Your tasks!"},
            "blocks": blocks,
        },
    )


if __name__ == "__main__":
    app.start(3000)  # POST http://localhost:3000/slack/events
