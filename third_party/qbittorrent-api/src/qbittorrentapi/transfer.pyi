from typing import Iterable
from typing import Optional
from typing import Text

from qbittorrentapi._types import JsonValueT
from qbittorrentapi._types import KwargsT
from qbittorrentapi.app import AppAPIMixIn
from qbittorrentapi.definitions import ClientCache
from qbittorrentapi.definitions import Dictionary

# mypy crashes when this is imported from _types...
JsonDictionaryT = Dictionary[Text, JsonValueT]

class TransferInfoDictionary(JsonDictionaryT): ...

class Transfer(ClientCache):
    @property
    def info(self) -> TransferInfoDictionary: ...
    @property
    def speed_limits_mode(self) -> Text: ...
    @speed_limits_mode.setter
    def speed_limits_mode(self, v: Text | int) -> None: ...
    @property
    def speedLimitsMode(self) -> Text: ...
    @speedLimitsMode.setter
    def speedLimitsMode(self, v: Text | int) -> None: ...
    def set_speed_limits_mode(
        self,
        intended_state: Optional[bool] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    setSpeedLimitsMode = set_speed_limits_mode
    def toggleSpeedLimitsMode(
        self,
        intended_state: Optional[bool] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    def toggle_speed_limits_mode(
        self,
        intended_state: Optional[bool] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    @property
    def download_limit(self) -> int: ...
    @download_limit.setter
    def download_limit(self, v: Text | int) -> None: ...
    @property
    def downloadLimit(self) -> int: ...
    @downloadLimit.setter
    def downloadLimit(self, v: Text | int) -> None: ...
    @property
    def upload_limit(self) -> int: ...
    @upload_limit.setter
    def upload_limit(self, v: Text | int) -> None: ...
    @property
    def uploadLimit(self) -> int: ...
    @uploadLimit.setter
    def uploadLimit(self, v: Text | int) -> None: ...
    def set_download_limit(
        self,
        limit: Optional[Text | int] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    def setDownloadLimit(
        self,
        limit: Optional[Text | int] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    def set_upload_limit(
        self,
        limit: Optional[Text | int] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    def setUploadLimit(
        self,
        limit: Optional[Text | int] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    def ban_peers(
        self,
        peers: Optional[Text | Iterable[Text]] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    def banPeers(
        self,
        peers: Optional[Text | Iterable[Text]] = None,
        **kwargs: KwargsT,
    ) -> None: ...

class TransferAPIMixIn(AppAPIMixIn):
    @property
    def transfer(self) -> Transfer: ...
    def transfer_info(self, **kwargs: KwargsT) -> TransferInfoDictionary: ...
    def transfer_speed_limits_mode(self, **kwargs: KwargsT) -> str: ...
    def transfer_speedLimitsMode(self, **kwargs: KwargsT) -> str: ...
    def transfer_set_speed_limits_mode(
        self,
        intended_state: Optional[bool] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    def transfer_setSpeedLimitsMode(
        self,
        intended_state: Optional[bool] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    def transfer_toggleSpeedLimitsMode(
        self,
        intended_state: Optional[bool] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    def transfer_toggle_speed_limits_mode(
        self,
        intended_state: Optional[bool] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    def transfer_download_limit(self, **kwargs: KwargsT) -> int: ...
    def transfer_downloadLimit(self, **kwargs: KwargsT) -> int: ...
    def transfer_upload_limit(self, **kwargs: KwargsT) -> int: ...
    def transfer_uploadLimit(self, **kwargs: KwargsT) -> int: ...
    def transfer_set_download_limit(
        self,
        limit: Optional[Text | int] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    def transfer_setDownloadLimit(
        self,
        limit: Optional[Text | int] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    def transfer_set_upload_limit(
        self,
        limit: Optional[Text | int] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    def transfer_setUploadLimit(
        self,
        limit: Optional[Text | int] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    def transfer_ban_peers(
        self,
        peers: Optional[Text | Iterable[Text]] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    def transfer_banPeers(
        self,
        peers: Optional[Text | Iterable[Text]] = None,
        **kwargs: KwargsT,
    ) -> None: ...
