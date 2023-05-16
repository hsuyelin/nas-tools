# pytype: skip-file
import inspect
import logging
from typing import Callable, Dict, Optional, Any, Sequence

from slack_bolt.request import BoltRequest
from slack_bolt.response import BoltResponse
from .args import Args
from slack_bolt.request.payload_utils import (
    to_options,
    to_shortcut,
    to_action,
    to_view,
    to_command,
    to_event,
    to_message,
    to_step,
)
from ..logger.messages import warning_skip_uncommon_arg_name


def build_required_kwargs(
    *,
    logger: logging.Logger,
    required_arg_names: Sequence[str],
    request: BoltRequest,
    response: Optional[BoltResponse],
    next_func: Callable[[], None] = None,
    this_func: Optional[Callable] = None,
    error: Optional[Exception] = None,  # for error handlers
    next_keys_required: bool = True,  # False for listeners / middleware / error handlers
) -> Dict[str, Any]:
    all_available_args = {
        "logger": logger,
        "client": request.context.client,
        "req": request,
        "request": request,
        "resp": response,
        "response": response,
        "context": request.context,
        # payload
        "body": request.body,
        "options": to_options(request.body),
        "shortcut": to_shortcut(request.body),
        "action": to_action(request.body),
        "view": to_view(request.body),
        "command": to_command(request.body),
        "event": to_event(request.body),
        "message": to_message(request.body),
        "step": to_step(request.body),
        # utilities
        "ack": request.context.ack,
        "say": request.context.say,
        "respond": request.context.respond,
        # middleware
        "next": next_func,
        "next_": next_func,  # for the middleware using Python's built-in `next()` function
        # error handler
        "error": error,  # Exception
    }
    if not next_keys_required:
        all_available_args.pop("next")
        all_available_args.pop("next_")

    all_available_args["payload"] = (
        all_available_args["options"]
        or all_available_args["shortcut"]
        or all_available_args["action"]
        or all_available_args["view"]
        or all_available_args["command"]
        or all_available_args["event"]
        or all_available_args["message"]
        or all_available_args["step"]
        or request.body
    )
    for k, v in request.context.items():
        if k not in all_available_args:
            all_available_args[k] = v

    if len(required_arg_names) > 0:
        # To support instance/class methods in a class for listeners/middleware,
        # check if the first argument is either self or cls
        first_arg_name = required_arg_names[0]
        if first_arg_name in {"self", "cls"}:
            required_arg_names.pop(0)
        elif first_arg_name not in all_available_args.keys() and first_arg_name != "args":
            if this_func is None:
                logger.warning(warning_skip_uncommon_arg_name(first_arg_name))
                required_arg_names.pop(0)
            elif inspect.ismethod(this_func):
                # We are sure that we should skip manipulating this arg
                required_arg_names.pop(0)

    kwargs: Dict[str, Any] = {k: v for k, v in all_available_args.items() if k in required_arg_names}
    found_arg_names = kwargs.keys()
    for name in required_arg_names:
        if name == "args":
            if isinstance(request, BoltRequest):
                kwargs[name] = Args(**all_available_args)
            else:
                logger.warning(f"Unknown Request object type detected ({type(request)})")

        elif name not in found_arg_names:
            logger.warning(f"{name} is not a valid argument")
            kwargs[name] = None
    return kwargs
