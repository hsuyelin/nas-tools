from enum import Enum
from typing import Any
from typing import Optional
from typing import Text
from typing import Type
from typing import TypeVar

try:
    from collections import UserList
except ImportError:
    from UserList import UserList  # type: ignore

from qbittorrentapi._attrdict import AttrDict
from qbittorrentapi._types import DictInputT
from qbittorrentapi._types import JsonDictionaryT
from qbittorrentapi._types import KwargsT
from qbittorrentapi._types import ListInputT
from qbittorrentapi.client import Client
from qbittorrentapi.request import Request

K = TypeVar("K")
V = TypeVar("V")
ListEntryT = TypeVar("ListEntryT", bound=JsonDictionaryT)

class APINames(Enum):
    Authorization: Text
    Application: Text
    Log: Text
    Sync: Text
    Transfer: Text
    Torrents: Text
    RSS: Text
    Search: Text
    EMPTY: Text

class TorrentStates(Enum):
    ERROR: Text
    MISSING_FILES: Text
    UPLOADING: Text
    PAUSED_UPLOAD: Text
    QUEUED_UPLOAD: Text
    STALLED_UPLOAD: Text
    CHECKING_UPLOAD: Text
    FORCED_UPLOAD: Text
    ALLOCATING: Text
    DOWNLOADING: Text
    METADATA_DOWNLOAD: Text
    FORCED_METADATA_DOWNLOAD: Text
    PAUSED_DOWNLOAD: Text
    QUEUED_DOWNLOAD: Text
    FORCED_DOWNLOAD: Text
    STALLED_DOWNLOAD: Text
    CHECKING_DOWNLOAD: Text
    CHECKING_RESUME_DATA: Text
    MOVING: Text
    UNKNOWN: Text
    @property
    def is_downloading(self) -> bool: ...
    @property
    def is_uploading(self) -> bool: ...
    @property
    def is_complete(self) -> bool: ...
    @property
    def is_checking(self) -> bool: ...
    @property
    def is_errored(self) -> bool: ...
    @property
    def is_paused(self) -> bool: ...

class ClientCache:
    _client: Client
    def __init__(self, *args: Any, client: Request, **kwargs: KwargsT) -> None: ...

class Dictionary(ClientCache, AttrDict[K, V]):
    def __init__(
        self,
        data: Optional[DictInputT] = None,
        client: Optional[Request] = None,
    ): ...
    @classmethod
    def _normalize(cls, data: DictInputT) -> AttrDict[K, V]: ...

class List(ClientCache, UserList[ListEntryT]):
    def __init__(
        self,
        list_entries: Optional[ListInputT] = None,
        entry_class: Optional[Type[ListEntryT]] = None,
        client: Optional[Request] = None,
    ) -> None: ...

class ListEntry(JsonDictionaryT): ...
