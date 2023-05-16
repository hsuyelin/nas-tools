import time
import logging

from slack_sdk import WebClient
from slack_sdk.web import SlackResponse

from slack_bolt import App, Ack
from slack_bolt.workflows.step import Configure, Update, Complete, Fail, WorkflowStep

logging.basicConfig(level=logging.DEBUG)

# export SLACK_SIGNING_SECRET=***
# export SLACK_BOT_TOKEN=xoxb-***
app = App()


@app.middleware  # or app.use(log_request)
def log_request(logger, body, next):
    logger.debug(body)
    return next()


# https://api.slack.com/tutorials/workflow-builder-steps

copy_review_step = WorkflowStep.builder("copy_review")


@copy_review_step.edit
def edit(ack: Ack, step, configure: Configure):
    ack()
    configure(
        blocks=[
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
        ]
    )


@copy_review_step.save
def save(ack: Ack, step: dict, view: dict, update: Update):
    state_values = view["state"]["values"]
    update(
        inputs={
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
        outputs=[
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
    )
    ack()


pseudo_database = {}


def additional_matcher(step):
    email = str(step.get("inputs", {}).get("taskAuthorEmail"))
    if "@" not in email:
        return False
    return True


def noop_middleware(next):
    return next()


def notify_execution(client: WebClient, step: dict):
    time.sleep(5)
    client.chat_postMessage(channel="#random", text=f"Step execution: ```{step}```")


@copy_review_step.execute(
    matchers=[additional_matcher],
    middleware=[noop_middleware],
    lazy=[notify_execution],
)
def execute(step: dict, client: WebClient, complete: Complete, fail: Fail):
    try:
        complete(
            outputs={
                "taskName": step["inputs"]["taskName"]["value"],
                "taskDescription": step["inputs"]["taskDescription"]["value"],
                "taskAuthorEmail": step["inputs"]["taskAuthorEmail"]["value"],
            }
        )

        user_lookup: SlackResponse = client.users_lookupByEmail(email=step["inputs"]["taskAuthorEmail"]["value"])
        user_id = user_lookup["user"]["id"]
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

        client.views_publish(
            user_id=user_id,
            view={
                "type": "home",
                "title": {"type": "plain_text", "text": "Your tasks!"},
                "blocks": blocks,
            },
        )
    except Exception as err:
        fail(error={"message": f"Something wrong! {err}"})


app.step(copy_review_step)

if __name__ == "__main__":
    app.start(3000)  # POST http://localhost:3000/slack/events
