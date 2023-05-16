from abc import ABCMeta
from typing import Any
from typing import Dict
from typing import Mapping
from typing import MutableMapping
from typing import Text
from typing import TypeVar

K = TypeVar("K")
KOther = TypeVar("KOther")
V = TypeVar("V")
VOther = TypeVar("VOther")
KwargsT = Any

def merge(
    left: Mapping[K, V],
    right: Mapping[KOther, VOther],
) -> Dict[K | KOther, V | VOther]: ...

class Attr(Mapping[K, V], metaclass=ABCMeta):
    def __call__(self, key: K) -> V: ...
    def __getattr__(self, key: Text) -> V: ...
    def __add__(
        self,
        other: Mapping[KOther, VOther],
    ) -> Attr[K | KOther, V | VOther]: ...
    def __radd__(
        self,
        other: Mapping[KOther, VOther],
    ) -> Attr[K | KOther, V | VOther]: ...

class MutableAttr(Attr[K, V], MutableMapping[K, V], metaclass=ABCMeta):
    def __setattr__(self, key: Text, value: V) -> None: ...
    def __delattr__(self, key: Text, force: bool = ...) -> None: ...

class AttrDict(Dict[K, V], MutableAttr[K, V]):
    def __init__(self, *args: Any, **kwargs: KwargsT) -> None: ...
