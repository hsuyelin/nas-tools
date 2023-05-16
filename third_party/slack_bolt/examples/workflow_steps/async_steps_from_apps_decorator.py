import asyncio
import logging

from slack_sdk.web.async_client import AsyncSlackResponse, AsyncWebClient
from slack_bolt.async_app import AsyncApp, AsyncAck
from slack_bolt.workflows.step.async_step import (
    AsyncConfigure,
    AsyncUpdate,
    AsyncComplete,
    AsyncFail,
    AsyncWorkflowStep,
)

logging.basicConfig(level=logging.DEBUG)

# export SLACK_SIGNING_SECRET=***
# export SLACK_BOT_TOKEN=xoxb-***
app = AsyncApp()


# https://api.slack.com/tutorials/workflow-builder-steps

copy_review_step = AsyncWorkflowStep.builder("copy_review")


@copy_review_step.edit
async def edit(ack: AsyncAck, step: dict, configure: AsyncConfigure):
    await ack()
    await configure(
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
async def save(ack: AsyncAck, view: dict, update: AsyncUpdate):
    state_values = view["state"]["values"]
    await update(
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
    await ack()


pseudo_database = {}


async def additional_matcher(step):
    email = str(step.get("inputs", {}).get("taskAuthorEmail"))
    if "@" not in email:
        return False
    return True


async def noop_middleware(next):
    return await next()


async def notify_execution(client: AsyncWebClient, step: dict):
    await asyncio.sleep(5)
    await client.chat_postMessage(channel="#random", text=f"Step execution: ```{step}```")


@copy_review_step.execute(
    matchers=[additional_matcher],
    middleware=[noop_middleware],
    lazy=[notify_execution],
)
async def execute(step: dict, client: AsyncWebClient, complete: AsyncComplete, fail: AsyncFail):
    try:
        await complete(
            outputs={
                "taskName": step["inputs"]["taskName"]["value"],
                "taskDescription": step["inputs"]["taskDescription"]["value"],
                "taskAuthorEmail": step["inputs"]["taskAuthorEmail"]["value"],
            }
        )
        user_lookup: AsyncSlackResponse = await client.users_lookupByEmail(email=step["inputs"]["taskAuthorEmail"]["value"])
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

        await client.views_publish(
            user_id=user_id,
            view={
                "type": "home",
                "title": {"type": "plain_text", "text": "Your tasks!"},
                "blocks": blocks,
            },
        )
    except Exception as err:
        await fail(error={"message": f"Something wrong! {err}"})


app.step(copy_review_step)

if __name__ == "__main__":
    app.start(3000)  # POST http://localhost:3000/slack/events
