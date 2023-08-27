from enum import Enum
from typing import Any
from typing import Literal
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

class TorrentState(Enum):
    ERROR: Literal["error"]
    MISSING_FILES: Literal["missingFiles"]
    UPLOADING: Literal["uploading"]
    PAUSED_UPLOAD: Literal["pausedUP"]
    QUEUED_UPLOAD: Literal["queuedUP"]
    STALLED_UPLOAD: Literal["stalledUP"]
    CHECKING_UPLOAD: Literal["checkingUP"]
    FORCED_UPLOAD: Literal["forcedUP"]
    ALLOCATING: Literal["allocating"]
    DOWNLOADING: Literal["downloading"]
    METADATA_DOWNLOAD: Literal["metaDL"]
    FORCED_METADATA_DOWNLOAD: Literal["forcedMetaDL"]
    PAUSED_DOWNLOAD: Literal["pausedDL"]
    QUEUED_DOWNLOAD: Literal["queuedDL"]
    FORCED_DOWNLOAD: Literal["forcedDL"]
    STALLED_DOWNLOAD: Literal["stalledDL"]
    CHECKING_DOWNLOAD: Literal["checkingDL"]
    CHECKING_RESUME_DATA: Literal["checkingResumeData"]
    MOVING: Literal["moving"]
    UNKNOWN: Literal["unknown"]
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

TorrentStates = TorrentState

class TrackerStatus(Enum):
    DISABLED: Literal[0]
    NOT_CONTACTED: Literal[1]
    WORKING: Literal[2]
    UPDATING: Literal[3]
    NOT_WORKING: Literal[4]
    @property
    def display(self) -> Text: ...

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
