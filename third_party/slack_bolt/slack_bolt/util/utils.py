import copy
import inspect
import sys
from logging import Logger
from typing import Optional, Union, Dict, Any, Sequence, Callable, List

from slack_sdk import WebClient
from slack_sdk.models import JsonObject

from slack_bolt.error import BoltError
from slack_bolt.version import __version__ as bolt_version


def create_web_client(token: Optional[str] = None, logger: Optional[Logger] = None) -> WebClient:
    return WebClient(
        token=token,
        logger=logger,
        user_agent_prefix=f"Bolt/{bolt_version}",
    )


def convert_to_dict_list(objects: Sequence[Union[Dict, JsonObject]]) -> Sequence[Dict]:
    return [convert_to_dict(elm) for elm in objects]


def convert_to_dict(obj: Union[Dict, JsonObject]) -> Dict:
    if isinstance(obj, dict):
        return obj
    if isinstance(obj, JsonObject) or hasattr(obj, "to_dict"):
        return obj.to_dict()
    raise BoltError(f"{obj} (type: {type(obj)}) is unsupported")


def create_copy(original: Any) -> Any:
    if sys.version_info.major == 3 and sys.version_info.minor <= 6:
        # NOTE: Unfortunately, copy.deepcopy doesn't work in Python 3.6.5.
        # --------------------
        # >     rv = reductor(4)
        # E     TypeError: can't pickle _thread.RLock objects
        # ../../.pyenv/versions/3.6.10/lib/python3.6/copy.py:169: TypeError
        # --------------------
        # As a workaround, this operation uses shallow copies in Python 3.6.
        # If your code modifies the shared data in threads / async functions, race conditions may arise.
        # Please consider upgrading Python major version to 3.7+ if you encounter some issues due to this.
        return copy.copy(original)
    else:
        return copy.deepcopy(original)


def get_boot_message(development_server: bool = False) -> str:
    if sys.platform == "win32":
        # Some Windows environments may fail to parse this str value
        # and result in UnicodeEncodeError
        if development_server:
            return "Bolt app is running! (development server)"
        else:
            return "Bolt app is running!"

    try:
        if development_server:
            return "⚡️ Bolt app is running! (development server)"
        else:
            return "⚡️ Bolt app is running!"
    except ValueError:
        # ValueError is a runtime exception for a given value
        # It's a super class of UnicodeEncodeError, which may be raised in the scenario
        # see also: https://github.com/slackapi/bolt-python/issues/170
        if development_server:
            return "Bolt app is running! (development server)"
        else:
            return "Bolt app is running!"


def get_name_for_callable(func: Callable) -> str:
    """Returns the name for the given Callable function object.

    Args:
        func: Either a `Callable` instance or a function, which as `__name__`

    Returns:
        The name of the given Callable object
    """
    if hasattr(func, "__name__"):
        return func.__name__
    else:
        return f"{func.__class__.__module__}.{func.__class__.__name__}"


def get_arg_names_of_callable(func: Callable) -> List[str]:
    return inspect.getfullargspec(inspect.unwrap(func)).args
