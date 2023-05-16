from typing import Iterable
from typing import Optional
from typing import Text

from qbittorrentapi._types import DictInputT
from qbittorrentapi._types import JsonDictionaryT
from qbittorrentapi._types import KwargsT
from qbittorrentapi._types import ListInputT
from qbittorrentapi.app import AppAPIMixIn
from qbittorrentapi.definitions import ClientCache
from qbittorrentapi.definitions import List
from qbittorrentapi.definitions import ListEntry

class SearchJobDictionary(JsonDictionaryT):
    def __init__(
        self,
        data: DictInputT,
        client: SearchAPIMixIn,
    ) -> None: ...
    def stop(self, **kwargs: KwargsT) -> None: ...
    def status(self, **kwargs: KwargsT) -> SearchStatusesList: ...
    def results(
        self,
        limit: Optional[Text | int] = None,
        offset: Optional[Text | int] = None,
        **kwargs: KwargsT
    ) -> SearchResultsDictionary: ...
    def delete(self, **kwargs: KwargsT) -> None: ...

class SearchResultsDictionary(JsonDictionaryT): ...
class SearchStatus(ListEntry): ...

class SearchStatusesList(List[SearchStatus]):
    def __init__(
        self,
        list_entries: ListInputT,
        client: SearchAPIMixIn,
    ) -> None: ...

class SearchCategory(ListEntry): ...

class SearchCategoriesList(List[SearchCategory]):
    def __init__(
        self,
        list_entries: ListInputT,
        client: SearchAPIMixIn,
    ) -> None: ...

class SearchPlugin(ListEntry): ...

class SearchPluginsList(List[SearchPlugin]):
    def __init__(
        self,
        list_entries: ListInputT,
        client: SearchAPIMixIn,
    ) -> None: ...

class Search(ClientCache):
    def start(
        self,
        pattern: Optional[Text] = None,
        plugins: Optional[Iterable[Text]] = None,
        category: Optional[Text] = None,
        **kwargs: KwargsT
    ) -> SearchJobDictionary: ...
    def stop(
        self,
        search_id: Optional[Text | int] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    def status(
        self,
        search_id: Optional[Text | int] = None,
        **kwargs: KwargsT,
    ) -> SearchStatusesList: ...
    def results(
        self,
        search_id: Optional[Text | int] = None,
        limit: Optional[Text | int] = None,
        offset: Optional[Text | int] = None,
        **kwargs: KwargsT
    ) -> SearchResultsDictionary: ...
    def delete(
        self,
        search_id: Optional[Text | int] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    def categories(
        self,
        plugin_name: Optional[Text] = None,
        **kwargs: KwargsT,
    ) -> SearchCategoriesList: ...
    @property
    def plugins(self) -> SearchPluginsList: ...
    def install_plugin(
        self,
        sources: Optional[Iterable[Text]] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    installPlugin = install_plugin
    def uninstall_plugin(
        self,
        sources: Optional[Iterable[Text]] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    uninstallPlugin = uninstall_plugin
    def enable_plugin(
        self,
        plugins: Optional[Iterable[Text]] = None,
        enable: Optional[bool] = None,
        **kwargs: KwargsT
    ) -> None: ...
    enablePlugin = enable_plugin
    def update_plugins(self, **kwargs: KwargsT) -> None: ...
    updatePlugins = update_plugins

class SearchAPIMixIn(AppAPIMixIn):
    @property
    def search(self) -> Search: ...
    def search_start(
        self,
        pattern: Optional[Text] = None,
        plugins: Optional[Iterable[Text]] = None,
        category: Optional[Text] = None,
        **kwargs: KwargsT
    ) -> SearchJobDictionary: ...
    def search_stop(
        self,
        search_id: Optional[Text | int] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    def search_status(
        self,
        search_id: Optional[Text | int] = None,
        **kwargs: KwargsT,
    ) -> SearchStatusesList: ...
    def search_results(
        self,
        search_id: Optional[Text | int] = None,
        limit: Optional[Text | int] = None,
        offset: Optional[Text | int] = None,
        **kwargs: KwargsT
    ) -> SearchResultsDictionary: ...
    def search_delete(
        self,
        search_id: Optional[Text | int] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    def search_categories(
        self,
        plugin_name: Optional[Text] = None,
        **kwargs: KwargsT,
    ) -> SearchCategoriesList: ...
    def search_plugins(self, **kwargs: KwargsT) -> SearchPluginsList: ...
    def search_install_plugin(
        self,
        sources: Optional[Iterable[Text]] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    search_installPlugin = search_install_plugin
    def search_uninstall_plugin(
        self,
        names: Optional[Iterable[Text]] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    search_uninstallPlugin = search_uninstall_plugin
    def search_enable_plugin(
        self,
        plugins: Optional[Iterable[Text]] = None,
        enable: Optional[bool] = None,
        **kwargs: KwargsT
    ) -> None: ...
    search_enablePlugin = search_enable_plugin
    def search_update_plugins(self, **kwargs: KwargsT) -> None: ...
    search_updatePlugins = search_update_plugins
