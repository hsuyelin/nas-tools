import time
from typing import Union, Dict, Any, Optional

from slack_sdk.web import SlackResponse

from slack_bolt.request import BoltRequest
from slack_bolt.request.payload_utils import (
    is_action,
    is_event,
    is_options,
    is_shortcut,
    is_slash_command,
    is_view_submission,
    is_view_closed,
    is_workflow_step_edit,
    is_workflow_step_save,
    is_workflow_step_execute,
)

# -------------------------------
# Error
# -------------------------------


def error_client_invalid_type() -> str:
    return "`client` must be a slack_sdk.web.WebClient"


def error_client_invalid_type_async() -> str:
    return "`client` must be a slack_sdk.web.async_client.AsyncWebClient"


def error_oauth_flow_invalid_type_async() -> str:
    return "`oauth_flow` must be a slack_bolt.oauth.async_oauth_flow.AsyncOAuthFlow"


def error_oauth_settings_invalid_type_async() -> str:
    return "`oauth_settings` must be a slack_bolt.oauth.async_oauth_settings.AsyncOAuthSettings"


def error_auth_test_failure(error_response: SlackResponse) -> str:
    return f"`token` is invalid (auth.test result: {error_response})"


def error_token_required() -> str:
    return "Either an env variable `SLACK_BOT_TOKEN` " "or `token` argument in the constructor is required."


def error_unexpected_listener_middleware(middleware_type) -> str:
    return f"Unexpected value for a listener middleware: {middleware_type}"


def error_listener_function_must_be_coro_func(func_name: str) -> str:
    return f"The listener function ({func_name}) is not a coroutine function."


def error_authorize_conflicts() -> str:
    return "`authorize` in the top-level arguments is not allowed when you pass either `oauth_settings` or `oauth_flow`"


def error_message_event_type(event_type: str) -> str:
    return (
        f'Although the document mentions "{event_type}", '
        'it is not a valid event type. Use "message" instead. '
        "If you want to filter message events, you can use `event.channel_type` for it."
    )


def error_installation_store_required_for_builtin_listeners() -> str:
    return (
        "To use the event listeners for token revocation handling, "
        "setting a valid `installation_store` to `App`/`AsyncApp` is required."
    )


# -------------------------------
# Warning
# -------------------------------


def warning_client_prioritized_and_token_skipped() -> str:
    return "As you gave `client` as well, `token` will be unused."


def warning_token_skipped() -> str:
    return (
        "As `installation_store` or `authorize` has been used, " "`token` (or SLACK_BOT_TOKEN env variable) will be ignored."
    )


def warning_installation_store_conflicts() -> str:
    return "As you gave both `installation_store` and `oauth_settings`/`auth_flow`, the top level one is unused."


def warning_unhandled_by_global_middleware(  # type: ignore
    name: str, req: Union[BoltRequest, "AsyncBoltRequest"]  # type: ignore
) -> str:  # type: ignore
    return (
        f"A global middleware ({name}) skipped calling either `next()` or `next_()` "
        f"without providing a response for the request ({req.body})"
    )


_unhandled_request_suggestion_prefix = """
---
[Suggestion] You can handle this type of event with the following listener function:
"""


def _build_filtered_body(body: Optional[Dict[str, Any]]) -> dict:
    if body is None:
        return {}

    payload_type = body.get("type")
    filtered_body = {"type": payload_type}

    if "view" in body:
        view = body["view"]
        # view_submission, view_closed, workflow_step_save
        filtered_body["view"] = {
            "type": view.get("type"),
            "callback_id": view.get("callback_id"),
        }

    if payload_type == "block_actions":
        # Block Kit Interactivity
        actions = body.get("actions", [])
        if len(actions) > 0 and actions[0] is not None:
            filtered_body["block_id"] = actions[0].get("block_id")
            filtered_body["action_id"] = actions[0].get("action_id")
    if payload_type == "block_suggestion":
        # Block Kit - external data source
        filtered_body["block_id"] = body.get("block_id")
        filtered_body["action_id"] = body.get("action_id")
        filtered_body["value"] = body.get("value")

    if payload_type == "event_callback" and "event" in body:
        # Events API, workflow_step_execute
        event_payload = body.get("event", {})
        filtered_event = {"type": event_payload.get("type")}
        if "subtype" in body["event"]:
            filtered_event["subtype"] = event_payload.get("subtype")
        filtered_body["event"] = filtered_event

    if "command" in body:
        # Slash Commands
        filtered_body["command"] = body.get("command")

    if payload_type in ["workflow_step_edit", "shortcut", "message_action"]:
        # Workflow Steps, Global Shortcuts, Message Shortcuts
        filtered_body["callback_id"] = body.get("callback_id")

    if payload_type == "interactive_message":
        # Actions in Attachments
        filtered_body["callback_id"] = body.get("callback_id")
        filtered_body["actions"] = body.get("actions")

    if payload_type == "dialog_suggestion":
        # Dialogs - external data source
        filtered_body["callback_id"] = body.get("callback_id")
        filtered_body["value"] = body.get("value")
    if payload_type == "dialog_submission":
        # Dialogs - clicking submit button
        filtered_body["callback_id"] = body.get("callback_id")
        filtered_body["submission"] = body.get("submission")
    if payload_type == "dialog_cancellation":
        # Dialogs - clicking cancel button
        filtered_body["callback_id"] = body.get("callback_id")

    return filtered_body


def _build_unhandled_request_suggestion(default_message: str, code_snippet: str):
    return f"""{default_message}{_unhandled_request_suggestion_prefix}{code_snippet}"""


def warning_unhandled_request(  # type: ignore
    req: Union[BoltRequest, "AsyncBoltRequest"],  # type: ignore
) -> str:  # type: ignore
    filtered_body = _build_filtered_body(req.body)
    default_message = f"Unhandled request ({filtered_body})"
    is_async = type(req) != BoltRequest
    if is_workflow_step_edit(req.body) or is_workflow_step_save(req.body) or is_workflow_step_execute(req.body):
        # @app.step
        callback_id = (
            filtered_body.get("callback_id")
            or filtered_body.get("view", {}).get("callback_id")  # type: ignore
            or "your-callback-id"
        )
        return _build_unhandled_request_suggestion(
            default_message,
            f"""
from slack_bolt.workflows.step{'.async_step' if is_async else ''} import {'Async' if is_async else ''}WorkflowStep
ws = {'Async' if is_async else ''}WorkflowStep(
    callback_id="{callback_id}",
    edit=edit,
    save=save,
    execute=execute,
)
# Pass Step to set up listeners
app.step(ws)
""",
        )
    if is_action(req.body):
        # @app.action
        action_id_or_callback_id = req.body.get("callback_id")
        if req.body.get("type") == "block_actions":
            action_id_or_callback_id = req.body.get("actions")[0].get("action_id")
        return _build_unhandled_request_suggestion(
            default_message,
            f"""
@app.action("{action_id_or_callback_id}")
{'async ' if is_async else ''}def handle_some_action(ack, body, logger):
    {'await ' if is_async else ''}ack()
    logger.info(body)
""",
        )
    if is_options(req.body):
        # @app.options
        constraints = '"action-id"'
        if req.body.get("action_id") is not None:
            constraints = '"' + req.body.get("action_id") + '"'
        elif req.body.get("type") == "dialog_suggestion":
            constraints = f"""{{"type": "dialog_suggestion", "callback_id": "{req.body.get('callback_id')}"}}"""
        return _build_unhandled_request_suggestion(
            default_message,
            f"""
@app.options({constraints})
{'async ' if is_async else ''}def handle_some_options(ack):
    {'await ' if is_async else ''}ack(options=[ ... ])
""",
        )
    if is_shortcut(req.body):
        # @app.shortcut
        id = req.body.get("action_id") or req.body.get("callback_id")
        return _build_unhandled_request_suggestion(
            default_message,
            f"""
@app.shortcut("{id}")
{'async ' if is_async else ''}def handle_shortcuts(ack, body, logger):
    {'await ' if is_async else ''}ack()
    logger.info(body)
""",
        )
    if is_view_submission(req.body):
        # @app.view
        return _build_unhandled_request_suggestion(
            default_message,
            f"""
@app.view("{req.body.get('view', {}).get('callback_id', 'modal-view-id')}")
{'async ' if is_async else ''}def handle_view_submission_events(ack, body, logger):
    {'await ' if is_async else ''}ack()
    logger.info(body)
""",
        )
    if is_view_closed(req.body):
        # @app.view
        return _build_unhandled_request_suggestion(
            default_message,
            f"""
@app.view_closed("{req.body.get('view', {}).get('callback_id', 'modal-view-id')}")
{'async ' if is_async else ''}def handle_view_closed_events(ack, body, logger):
    {'await ' if is_async else ''}ack()
    logger.info(body)
""",
        )
    if is_event(req.body):
        # @app.event
        event_type = req.body.get("event", {}).get("type")
        return _build_unhandled_request_suggestion(
            default_message,
            f"""
@app.event("{event_type}")
{'async ' if is_async else ''}def handle_{event_type}_events(body, logger):
    logger.info(body)
""",
        )
    if is_slash_command(req.body):
        # @app.command
        command = req.body.get("command", "/your-command")
        return _build_unhandled_request_suggestion(
            default_message,
            f"""
@app.command("{command}")
{'async ' if is_async else ''}def handle_some_command(ack, body, logger):
    {'await ' if is_async else ''}ack()
    logger.info(body)
""",
        )
    return default_message


def warning_did_not_call_ack(listener_name: str) -> str:
    return f"{listener_name} didn't call ack()"


def warning_bot_only_conflicts() -> str:
    return (
        "installation_store_bot_only exists in both App and OAuthFlow.settings. "
        "The one passed in App constructor is used."
    )


def warning_skip_uncommon_arg_name(arg_name: str) -> str:
    return (
        f"Bolt skips injecting a value to the first keyword argument ({arg_name}). "
        "If it is self/cls of a method, we recommend using the common names."
    )


# -------------------------------
# Info
# -------------------------------


def info_default_oauth_settings_loaded() -> str:
    return (
        "As you've set SLACK_CLIENT_ID and SLACK_CLIENT_SECRET env variables, "
        "Bolt has enabled the file-based InstallationStore/OAuthStateStore for you. "
        "Note that these file-based stores are for local development. "
        "If you'd like to use a different data store, set the oauth_settings argument in the App constructor. "
        "Please refer to https://slack.dev/bolt-python/concepts#authenticating-oauth for more details."
    )


# -------------------------------
# Debug
# -------------------------------


def debug_applying_middleware(middleware_name: str) -> str:
    return f"Applying {middleware_name}"


def debug_checking_listener(listener_name: str) -> str:
    return f"Checking listener: {listener_name} ..."


def debug_running_listener(listener_name: str) -> str:
    return f"Running listener: {listener_name} ..."


def debug_running_lazy_listener(func_name: str) -> str:
    return f"Running lazy listener: {func_name} ..."


def debug_responding(status: int, body: str, millis: int) -> str:
    return f'Responding with status: {status} body: "{body}" ({millis} millis)'


def debug_return_listener_middleware_response(listener_name: str, status: int, body: str, starting_time: float) -> str:
    millis = int((time.time() - starting_time) * 1000)
    return (
        "Responding with listener middleware's response - "
        f"listener: {listener_name}, status: {status}, body: {body} ({millis} millis)"
    )
