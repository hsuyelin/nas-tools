# pytype: skip-file
import re
import sys
from logging import Logger

from slack_bolt.error import BoltError
from slack_bolt.request.payload_utils import (
    is_block_actions,
    is_global_shortcut,
    is_message_shortcut,
    is_attachment_action,
    is_dialog_submission,
    is_dialog_cancellation,
    is_workflow_step_edit,
    is_slash_command,
    is_event,
    is_view_submission,
    is_view_closed,
    is_block_suggestion,
    is_dialog_suggestion,
    is_shortcut,
    to_action,
    is_workflow_step_save,
)
from ..logger.messages import error_message_event_type
from ..util.utils import get_arg_names_of_callable

if sys.version_info.major == 3 and sys.version_info.minor <= 6:
    from re import _pattern_type as Pattern
else:
    from re import Pattern
from typing import Callable, Awaitable, Any, Sequence, Optional, Union, Dict

from slack_bolt.kwargs_injection import build_required_kwargs
from slack_bolt.request import BoltRequest
from slack_bolt.response import BoltResponse
from .listener_matcher import ListenerMatcher
from slack_bolt.logger import get_bolt_logger


# a.k.a Union[ListenerMatcher, "AsyncListenerMatcher"]
class BuiltinListenerMatcher(ListenerMatcher):
    def __init__(
        self,
        *,
        func: Callable[..., Union[bool, Awaitable[bool]]],
        base_logger: Optional[Logger] = None,
    ):
        self.func = func
        self.arg_names = get_arg_names_of_callable(func)
        self.logger = get_bolt_logger(self.func, base_logger)

    def matches(self, req: BoltRequest, resp: BoltResponse) -> bool:
        return self.func(
            **build_required_kwargs(
                logger=self.logger,
                required_arg_names=self.arg_names,
                request=req,
                response=resp,
                this_func=self.func,
            )
        )


def build_listener_matcher(
    func: Callable[..., bool],
    asyncio: bool,
    base_logger: Optional[Logger] = None,
) -> Union[ListenerMatcher, "AsyncListenerMatcher"]:
    if asyncio:
        from .async_builtins import AsyncBuiltinListenerMatcher

        async def async_fun(body: Dict[str, Any]) -> bool:
            return func(body)

        return AsyncBuiltinListenerMatcher(func=async_fun, base_logger=base_logger)
    else:
        return BuiltinListenerMatcher(func=func, base_logger=base_logger)


# -------------
# events


def event(
    constraints: Union[
        str,
        Pattern,
        Dict[str, Optional[Union[str, Sequence[Optional[Union[str, Pattern]]]]]],
    ],
    asyncio: bool = False,
    base_logger: Optional[Logger] = None,
) -> Union[ListenerMatcher, "AsyncListenerMatcher"]:
    if isinstance(constraints, (str, Pattern)):
        event_type: Union[str, Pattern] = constraints
        _verify_message_event_type(event_type)

        def func(body: Dict[str, Any]) -> bool:
            return is_event(body) and _matches(event_type, body["event"]["type"])

        return build_listener_matcher(func, asyncio, base_logger)

    elif "type" in constraints:
        _verify_message_event_type(constraints["type"])

        def func(body: Dict[str, Any]) -> bool:
            if is_event(body):
                return _check_event_subtype(
                    event_payload=body["event"],
                    constraints=constraints,
                )
            return False

        return build_listener_matcher(func, asyncio, base_logger)

    raise BoltError(f"event ({constraints}: {type(constraints)}) must be any of str, Pattern, and dict")


def message_event(
    constraints: Dict[str, Optional[Union[str, Sequence[Optional[Union[str, Pattern]]]]]],
    keyword: Union[str, Pattern],
    asyncio: bool = False,
    base_logger: Optional[Logger] = None,
) -> Union[ListenerMatcher, "AsyncListenerMatcher"]:
    if "type" in constraints and keyword is not None:
        _verify_message_event_type(constraints["type"])

        def func(body: Dict[str, Any]) -> bool:
            if is_event(body):
                is_valid_subtype = _check_event_subtype(
                    event_payload=body["event"],
                    constraints=constraints,
                )
                if is_valid_subtype is True:
                    # Check keyword matching
                    text = body.get("event", {}).get("text", "")
                    match_result = re.findall(keyword, text)
                    if match_result is not None and match_result != []:
                        return True
            return False

        return build_listener_matcher(func, asyncio, base_logger)

    raise BoltError(f"event ({constraints}: {type(constraints)}) must be dict")


def _check_event_subtype(event_payload: dict, constraints: dict) -> bool:
    if not _matches(constraints["type"], event_payload["type"]):
        return False
    if "subtype" in constraints:
        expected_subtype: Optional[Union[str, Sequence[Optional[Union[str, Pattern]]]]] = constraints["subtype"]
        if expected_subtype is None:
            # "subtype" in constraints is intentionally None for this pattern
            return "subtype" not in event_payload
        elif isinstance(expected_subtype, (str, Pattern)):
            return "subtype" in event_payload and _matches(expected_subtype, event_payload["subtype"])
        elif isinstance(expected_subtype, Sequence):
            subtypes: Sequence[Optional[Union[str, Pattern]]] = expected_subtype
            for expected in subtypes:
                actual: Optional[str] = event_payload.get("subtype")
                if expected is None:
                    if actual is None:
                        return True
                elif actual is not None and _matches(expected, actual):
                    return True
            return False
        else:
            return "subtype" in event_payload and _matches(expected_subtype, event_payload["subtype"])
    return True


def _verify_message_event_type(event_type: str) -> None:
    if isinstance(event_type, str) and event_type.startswith("message."):
        raise ValueError(error_message_event_type(event_type))
    if isinstance(event_type, Pattern) and "message\\." in event_type.pattern:
        raise ValueError(error_message_event_type(event_type))


def workflow_step_execute(
    callback_id: Union[str, Pattern],
    asyncio: bool = False,
    base_logger: Optional[Logger] = None,
) -> Union[ListenerMatcher, "AsyncListenerMatcher"]:
    def func(body: Dict[str, Any]) -> bool:
        return (
            is_event(body)
            and _matches("workflow_step_execute", body["event"]["type"])
            and "workflow_step" in body["event"]
            and _matches(callback_id, body["event"]["callback_id"])
        )

    return build_listener_matcher(func, asyncio, base_logger)


# -------------
# slash commands


def command(
    command: Union[str, Pattern],
    asyncio: bool = False,
    base_logger: Optional[Logger] = None,
) -> Union[ListenerMatcher, "AsyncListenerMatcher"]:
    def func(body: Dict[str, Any]) -> bool:
        return is_slash_command(body) and _matches(command, body["command"])

    return build_listener_matcher(func, asyncio, base_logger)


# -------------
# shortcuts


def shortcut(
    constraints: Union[str, Pattern, Dict[str, Union[str, Pattern]]],
    asyncio: bool = False,
    base_logger: Optional[Logger] = None,
) -> Union[ListenerMatcher, "AsyncListenerMatcher"]:
    if isinstance(constraints, (str, Pattern)):
        callback_id: Union[str, Pattern] = constraints

        def func(body: Dict[str, Any]) -> bool:
            return is_shortcut(body) and _matches(callback_id, body["callback_id"])

        return build_listener_matcher(func, asyncio, base_logger)

    elif "type" in constraints and "callback_id" in constraints:
        if constraints["type"] == "shortcut":
            return global_shortcut(constraints["callback_id"], asyncio)
        if constraints["type"] == "message_action":
            return message_shortcut(constraints["callback_id"], asyncio)

    raise BoltError(f"shortcut ({constraints}: {type(constraints)}) must be any of str, Pattern, and dict")


def global_shortcut(
    callback_id: Union[str, Pattern],
    asyncio: bool = False,
    base_logger: Optional[Logger] = None,
) -> Union[ListenerMatcher, "AsyncListenerMatcher"]:
    def func(body: Dict[str, Any]) -> bool:
        return is_global_shortcut(body) and _matches(callback_id, body["callback_id"])

    return build_listener_matcher(func, asyncio, base_logger)


def message_shortcut(
    callback_id: Union[str, Pattern],
    asyncio: bool = False,
    base_logger: Optional[Logger] = None,
) -> Union[ListenerMatcher, "AsyncListenerMatcher"]:
    def func(body: Dict[str, Any]) -> bool:
        return is_message_shortcut(body) and _matches(callback_id, body["callback_id"])

    return build_listener_matcher(func, asyncio, base_logger)


# -------------
# action


def action(
    constraints: Union[str, Pattern, Dict[str, Union[str, Pattern]]],
    asyncio: bool = False,
    base_logger: Optional[Logger] = None,
) -> Union[ListenerMatcher, "AsyncListenerMatcher"]:
    if isinstance(constraints, (str, Pattern)):

        def func(body: Dict[str, Any]) -> bool:
            return (
                _block_action(constraints, body)
                or _attachment_action(constraints, body)
                or _dialog_submission(constraints, body)
                or _dialog_cancellation(constraints, body)
                or _workflow_step_edit(constraints, body)
            )

        return build_listener_matcher(func, asyncio, base_logger)

    elif "type" in constraints:
        action_type = constraints["type"]
        if action_type == "block_actions":
            return block_action(constraints, asyncio)
        if action_type == "interactive_message":
            return attachment_action(constraints["callback_id"], asyncio)
        if action_type == "dialog_submission":
            return dialog_submission(constraints["callback_id"], asyncio)
        if action_type == "dialog_cancellation":
            return dialog_cancellation(constraints["callback_id"], asyncio)
        # https://api.slack.com/workflows/steps
        if action_type == "workflow_step_edit":
            return workflow_step_edit(constraints["callback_id"], asyncio)

        raise BoltError(f"type: {action_type} is unsupported")
    elif "action_id" in constraints:
        # The default value is "block_actions"
        return block_action(constraints, asyncio)

    raise BoltError(f"action ({constraints}: {type(constraints)}) must be any of str, Pattern, and dict")


def _block_action(
    constraints: Union[str, Pattern, Dict[str, Union[str, Pattern]]],
    body: Dict[str, Any],
) -> bool:
    if is_block_actions(body) is False:
        return False

    action = to_action(body)
    if isinstance(constraints, (str, Pattern)):
        action_id = constraints
        return _matches(action_id, action["action_id"])
    elif isinstance(constraints, dict):
        # block_id matching is optional
        block_id: Optional[Union[str, Pattern]] = constraints.get("block_id")
        block_id_matched = block_id is None or _matches(block_id, action.get("block_id"))
        action_id_matched = _matches(constraints["action_id"], action["action_id"])
        return block_id_matched and action_id_matched


def block_action(
    constraints: Union[str, Pattern, Dict[str, Union[str, Pattern]]],
    asyncio: bool = False,
    base_logger: Optional[Logger] = None,
) -> Union[ListenerMatcher, "AsyncListenerMatcher"]:
    def func(body: Dict[str, Any]) -> bool:
        return _block_action(constraints, body)

    return build_listener_matcher(func, asyncio, base_logger)


def _attachment_action(
    callback_id: Union[str, Pattern],
    body: Dict[str, Any],
) -> bool:
    return is_attachment_action(body) and _matches(callback_id, body["callback_id"])


def attachment_action(
    callback_id: Union[str, Pattern],
    asyncio: bool = False,
    base_logger: Optional[Logger] = None,
) -> Union[ListenerMatcher, "AsyncListenerMatcher"]:
    def func(body: Dict[str, Any]) -> bool:
        return _attachment_action(callback_id, body)

    return build_listener_matcher(func, asyncio, base_logger)


def _dialog_submission(
    callback_id: Union[str, Pattern],
    body: Dict[str, Any],
) -> bool:
    return is_dialog_submission(body) and _matches(callback_id, body["callback_id"])


def dialog_submission(
    callback_id: Union[str, Pattern],
    asyncio: bool = False,
    base_logger: Optional[Logger] = None,
) -> Union[ListenerMatcher, "AsyncListenerMatcher"]:
    def func(body: Dict[str, Any]) -> bool:
        return _dialog_submission(callback_id, body)

    return build_listener_matcher(func, asyncio, base_logger)


def _dialog_cancellation(
    callback_id: Union[str, Pattern],
    body: Dict[str, Any],
) -> bool:
    return is_dialog_cancellation(body) and _matches(callback_id, body["callback_id"])


def dialog_cancellation(
    callback_id: Union[str, Pattern],
    asyncio: bool = False,
    base_logger: Optional[Logger] = None,
) -> Union[ListenerMatcher, "AsyncListenerMatcher"]:
    def func(body: Dict[str, Any]) -> bool:
        return _dialog_cancellation(callback_id, body)

    return build_listener_matcher(func, asyncio, base_logger)


def _workflow_step_edit(
    callback_id: Union[str, Pattern],
    body: Dict[str, Any],
) -> bool:
    return is_workflow_step_edit(body) and _matches(callback_id, body["callback_id"])


def workflow_step_edit(
    callback_id: Union[str, Pattern],
    asyncio: bool = False,
    base_logger: Optional[Logger] = None,
) -> Union[ListenerMatcher, "AsyncListenerMatcher"]:
    def func(body: Dict[str, Any]) -> bool:
        return _workflow_step_edit(callback_id, body)

    return build_listener_matcher(func, asyncio, base_logger)


# -------------------------
# view


def view(
    constraints: Union[str, Pattern, Dict[str, Union[str, Pattern]]],
    asyncio: bool = False,
    base_logger: Optional[Logger] = None,
) -> Union[ListenerMatcher, "AsyncListenerMatcher"]:
    if isinstance(constraints, (str, Pattern)):
        return view_submission(constraints, asyncio)
    elif "type" in constraints:
        if constraints["type"] == "view_submission":
            return view_submission(constraints["callback_id"], asyncio)
        if constraints["type"] == "view_closed":
            return view_closed(constraints["callback_id"], asyncio)

    raise BoltError(f"view ({constraints}: {type(constraints)}) must be any of str, Pattern, and dict")


def view_submission(
    callback_id: Union[str, Pattern],
    asyncio: bool = False,
    base_logger: Optional[Logger] = None,
) -> Union[ListenerMatcher, "AsyncListenerMatcher"]:
    def func(body: Dict[str, Any]) -> bool:
        return is_view_submission(body) and _matches(callback_id, body["view"]["callback_id"])

    return build_listener_matcher(func, asyncio, base_logger)


def view_closed(
    callback_id: Union[str, Pattern],
    asyncio: bool = False,
    base_logger: Optional[Logger] = None,
) -> Union[ListenerMatcher, "AsyncListenerMatcher"]:
    def func(body: Dict[str, Any]) -> bool:
        return is_view_closed(body) and _matches(callback_id, body["view"]["callback_id"])

    return build_listener_matcher(func, asyncio, base_logger)


def workflow_step_save(
    callback_id: Union[str, Pattern],
    asyncio: bool = False,
    base_logger: Optional[Logger] = None,
) -> Union[ListenerMatcher, "AsyncListenerMatcher"]:
    def func(body: Dict[str, Any]) -> bool:
        return is_workflow_step_save(body) and _matches(callback_id, body["view"]["callback_id"])

    return build_listener_matcher(func, asyncio, base_logger)


# -------------
# options


def options(
    constraints: Union[str, Pattern, Dict[str, Union[str, Pattern]]],
    asyncio: bool = False,
    base_logger: Optional[Logger] = None,
) -> Union[ListenerMatcher, "AsyncListenerMatcher"]:
    if isinstance(constraints, (str, Pattern)):

        def func(body: Dict[str, Any]) -> bool:
            return _block_suggestion(constraints, body) or _dialog_suggestion(constraints, body)

        return build_listener_matcher(func, asyncio, base_logger)

    if "action_id" in constraints:
        return block_suggestion(constraints["action_id"], asyncio)
    if "callback_id" in constraints:
        return dialog_suggestion(constraints["callback_id"], asyncio)
    else:
        raise BoltError(f"options ({constraints}: {type(constraints)}) must be any of str, Pattern, and dict")


def _block_suggestion(
    action_id: Union[str, Pattern],
    body: Dict[str, Any],
) -> bool:
    return is_block_suggestion(body) and _matches(action_id, body["action_id"])


def block_suggestion(
    action_id: Union[str, Pattern],
    asyncio: bool = False,
    base_logger: Optional[Logger] = None,
) -> Union[ListenerMatcher, "AsyncListenerMatcher"]:
    def func(body: Dict[str, Any]) -> bool:
        return _block_suggestion(action_id, body)

    return build_listener_matcher(func, asyncio, base_logger)


def _dialog_suggestion(
    callback_id: Union[str, Pattern],
    body: Dict[str, Any],
) -> bool:
    return is_dialog_suggestion(body) and _matches(callback_id, body["callback_id"])


def dialog_suggestion(
    callback_id: Union[str, Pattern],
    asyncio: bool = False,
    base_logger: Optional[Logger] = None,
) -> Union[ListenerMatcher, "AsyncListenerMatcher"]:
    def func(body: Dict[str, Any]) -> bool:
        return _dialog_suggestion(callback_id, body)

    return build_listener_matcher(func, asyncio, base_logger)


# -------------------------


def _matches(str_or_pattern: Union[str, Pattern], input: Optional[str]) -> bool:
    if str_or_pattern is None or input is None:
        return False

    if isinstance(str_or_pattern, str):
        exact_match_str: str = str_or_pattern
        return input == exact_match_str
    elif isinstance(str_or_pattern, Pattern):
        pattern: Pattern = str_or_pattern
        return pattern.search(input) is not None
    else:
        raise BoltError(f"{str_or_pattern} ({type(str_or_pattern)}) must be either str or Pattern")
