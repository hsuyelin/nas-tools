from typing import Dict, Any, Optional


# ------------------------------------------
# Public Utilities
# ------------------------------------------

# -------------------
# Events API
# -------------------


def to_event(body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    return body["event"] if is_event(body) else None


def to_message(body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if is_event(body) and body["event"]["type"] == "message":
        return to_event(body)
    return None


def is_event(body: Dict[str, Any]) -> bool:
    return body is not None and _is_expected_type(body, "event_callback") and "event" in body and "type" in body["event"]


def is_workflow_step_execute(body: Dict[str, Any]) -> bool:
    return is_event(body) and body["event"]["type"] == "workflow_step_execute" and "workflow_step" in body["event"]


# -------------------
# Slash Commands
# -------------------


def to_command(body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    return body if is_slash_command(body) else None


def is_slash_command(body: Dict[str, Any]) -> bool:
    return body is not None and "command" in body


# -------------------
# Actions
# -------------------


def to_action(body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if is_action(body):
        if is_block_actions(body) or is_attachment_action(body):
            return body["actions"][0]
        else:
            return body
    return None


def is_action(body: Dict[str, Any]) -> bool:
    return (
        is_attachment_action(body)
        or is_block_actions(body)
        or is_dialog_submission(body)
        or is_dialog_cancellation(body)
        or is_workflow_step_edit(body)
    )


def is_attachment_action(body: Dict[str, Any]) -> bool:
    return body is not None and _is_expected_type(body, "interactive_message") and "callback_id" in body


def is_block_actions(body: Dict[str, Any]) -> bool:
    return body is not None and _is_expected_type(body, "block_actions") and "actions" in body


def is_dialog_submission(body: Dict[str, Any]) -> bool:
    return body is not None and _is_expected_type(body, "dialog_submission") and "callback_id" in body


def is_dialog_cancellation(body: Dict[str, Any]) -> bool:
    return body is not None and _is_expected_type(body, "dialog_cancellation") and "callback_id" in body


def is_workflow_step_edit(body: Dict[str, Any]) -> bool:
    return body is not None and _is_expected_type(body, "workflow_step_edit") and "callback_id" in body


# -------------------
# Options
# -------------------


def to_options(body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if is_options(body):
        return body
    return None


def is_options(body: Dict[str, Any]) -> bool:
    return is_block_suggestion(body) or is_dialog_suggestion(body)


def is_block_suggestion(body: Dict[str, Any]) -> bool:
    return body is not None and _is_expected_type(body, "block_suggestion") and "action_id" in body


def is_dialog_suggestion(body: Dict[str, Any]) -> bool:
    return body is not None and _is_expected_type(body, "dialog_suggestion") and "callback_id" in body


# -------------------
# Shortcut
# -------------------


def to_shortcut(body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if is_shortcut(body):
        return body
    return None


def is_shortcut(body: Dict[str, Any]) -> bool:
    return is_global_shortcut(body) or is_message_shortcut(body)


def is_global_shortcut(body: Dict[str, Any]) -> bool:
    return body is not None and _is_expected_type(body, "shortcut") and "callback_id" in body


def is_message_shortcut(body: Dict[str, Any]) -> bool:
    return body is not None and _is_expected_type(body, "message_action") and "callback_id" in body


# -------------------
# View
# -------------------


def to_view(body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if is_view(body):
        return body["view"]
    return None


def is_view(body: Dict[str, Any]) -> bool:
    return is_view_submission(body) or is_view_closed(body)


def is_view_submission(body: Dict[str, Any]) -> bool:
    return (
        body is not None and _is_expected_type(body, "view_submission") and "view" in body and "callback_id" in body["view"]
    )


def is_view_closed(body: Dict[str, Any]) -> bool:
    return body is not None and _is_expected_type(body, "view_closed") and "view" in body and "callback_id" in body["view"]


def is_workflow_step_save(body: Dict[str, Any]) -> bool:
    return is_view_submission(body) and body["view"]["type"] == "workflow_step"


# -------------------
# Workflow Steps
# -------------------


def to_step(body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    # edit
    if is_workflow_step_edit(body):
        return body["workflow_step"]
    # save
    if is_workflow_step_save(body):
        return body["workflow_step"]
    # execute
    if is_workflow_step_execute(body):
        return body["event"]["workflow_step"]
    return None


# ------------------------------------------
# Internal Utilities
# ------------------------------------------


def _is_expected_type(body: dict, expected: str) -> bool:
    return body is not None and "type" in body and body["type"] == expected
