from logging import Logger
from typing import Optional
from typing import Text

from qbittorrentapi._types import KwargsT
from qbittorrentapi.definitions import ClientCache
from qbittorrentapi.request import Request

logger: Logger

class Authorization(ClientCache):
    @property
    def is_logged_in(self) -> bool: ...
    def log_in(
        self,
        username: Optional[Text] = None,
        password: Optional[Text] = None,
        **kwargs: KwargsT
    ) -> None: ...
    def log_out(self, **kwargs: KwargsT) -> None: ...

class AuthAPIMixIn(Request):
    @property
    def auth(self) -> Authorization: ...
    @property
    def authorization(self) -> Authorization: ...
    @property
    def is_logged_in(self) -> bool: ...
    def auth_log_in(
        self,
        username: Optional[Text] = None,
        password: Optional[Text] = None,
        **kwargs: KwargsT
    ) -> None: ...
    @property
    def _SID(self) -> Optional[Text]: ...
    def _session_cookie(self, cookie_name: Text = "SID") -> Optional[Text]: ...
    def auth_log_out(self, **kwargs: KwargsT) -> None: ...
