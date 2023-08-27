from typing import Any, Dict, Tuple, Union, TypeVar, Optional, NamedTuple

from typing_extensions import Literal

_Number = Union[int, float]
_Timeout = Optional[Union[_Number, Tuple[_Number, _Number]]]

T = TypeVar("T")


class Container:
    fields: Dict[str, Any]  #: raw fields

    def __init__(self, *, fields: Dict[str, Any]):
        self.fields = fields

    def get(self, key: str, default: Optional[T] = None) -> Any:
        """get the raw value by the **raw rpc response key**"""
        return self.fields.get(key, default)


class File(NamedTuple):
    name: str  # file name
    size: int  # file size in bytes
    completed: int  # bytes completed
    priority: Literal["high", "normal", "low"]
    selected: bool  # if selected for download
    id: int  # id of the file of this torrent, not should not be used outside the torrent scope.


class Group(Container):
    @property
    def name(self) -> str:
        return self.fields["name"]

    @property
    def honors_session_limits(self) -> bool:
        return self.fields["honorsSessionLimits"]

    @property
    def speed_limit_down_enabled(self) -> bool:
        return self.fields["speed-limit-down-enabled"]

    @property
    def speed_limit_down(self) -> int:
        return self.fields["speed-limit-down"]

    @property
    def speed_limit_up_enabled(self) -> bool:
        return self.fields["speed-limit-up-enabled"]

    @property
    def speed_limit_up(self) -> int:
        return self.fields["speed-limit-up"]
