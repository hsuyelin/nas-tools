from typing import Dict
from typing import Optional
from typing import Set
from typing import Text

from pkg_resources.extern.packaging.version import Version as _Version  # type: ignore

MOST_RECENT_SUPPORTED_APP_VERSION: Text
MOST_RECENT_SUPPORTED_API_VERSION: Text
APP_VERSION_2_API_VERSION_MAP: Dict[Text, Text]

def v(version: Text) -> _Version: ...  # type: ignore

class Version:
    _supported_app_versions: Optional[Set[str]] = None
    _supported_api_versions: Optional[Set[str]] = None
    @classmethod
    def supported_app_versions(cls) -> Set[str]: ...
    @classmethod
    def supported_api_versions(cls) -> Set[str]: ...
    @classmethod
    def is_app_version_supported(cls, app_version: Text) -> bool: ...
    @classmethod
    def is_api_version_supported(cls, api_version: Text) -> bool: ...
    @classmethod
    def latest_supported_app_version(cls) -> str: ...
    @classmethod
    def latest_supported_api_version(cls) -> str: ...
