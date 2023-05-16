from typing import Optional
from typing import Text

from qbittorrentapi._types import JsonValueT
from qbittorrentapi._types import KwargsT
from qbittorrentapi.app import AppAPIMixIn
from qbittorrentapi.definitions import ClientCache
from qbittorrentapi.definitions import Dictionary

# mypy crashes when this is imported from _types...
JsonDictionaryT = Dictionary[Text, JsonValueT]

class SyncMainDataDictionary(JsonDictionaryT): ...
class SyncTorrentPeersDictionary(JsonDictionaryT): ...

class Sync(ClientCache):
    maindata: _MainData
    torrent_peers: _TorrentPeers
    torrentPeers: _TorrentPeers
    def __init__(self, client: SyncAPIMixIn) -> None: ...

    class _MainData(ClientCache):
        _rid: int | None
        def __init__(self, client: SyncAPIMixIn) -> None: ...
        def __call__(
            self,
            rid: Optional[Text | int] = None,
            **kwargs: KwargsT,
        ) -> SyncMainDataDictionary: ...
        def delta(self, **kwargs: KwargsT) -> SyncMainDataDictionary: ...
        def reset_rid(self) -> None: ...

    class _TorrentPeers(ClientCache):
        _rid: int | None
        def __init__(self, client: SyncAPIMixIn) -> None: ...
        def __call__(
            self,
            torrent_hash: Optional[Text] = None,
            rid: Optional[Text | int] = None,
            **kwargs: KwargsT
        ) -> SyncTorrentPeersDictionary: ...
        def delta(
            self,
            torrent_hash: Optional[Text] = None,
            **kwargs: KwargsT,
        ) -> SyncTorrentPeersDictionary: ...
        def reset_rid(self) -> None: ...

class SyncAPIMixIn(AppAPIMixIn):
    @property
    def sync(self) -> Sync: ...
    def sync_maindata(
        self,
        rid: Text | int = 0,
        **kwargs: KwargsT,
    ) -> SyncMainDataDictionary: ...
    def sync_torrent_peers(
        self,
        torrent_hash: Optional[Text] = None,
        rid: Text | int = 0,
        **kwargs: KwargsT
    ) -> SyncTorrentPeersDictionary: ...
    sync_torrentPeers = sync_torrent_peers
