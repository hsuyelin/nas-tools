from typing import Mapping
from typing import Optional
from typing import Text

from qbittorrentapi._types import JsonDictionaryT
from qbittorrentapi._types import JsonValueT
from qbittorrentapi._types import KwargsT
from qbittorrentapi.app import AppAPIMixIn
from qbittorrentapi.definitions import ClientCache

class RSSitemsDictionary(JsonDictionaryT): ...
class RSSRulesDictionary(JsonDictionaryT): ...

class RSS(ClientCache):
    items: _Items
    def __init__(self, client: RSSAPIMixIn) -> None: ...
    def add_folder(
        self,
        folder_path: Optional[Text] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    addFolder = add_folder
    def add_feed(
        self,
        url: Optional[Text] = None,
        item_path: Optional[Text] = None,
        **kwargs: KwargsT
    ) -> None: ...
    addFeed = add_feed
    def remove_item(
        self,
        item_path: Optional[Text] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    removeItem = remove_item
    def move_item(
        self,
        orig_item_path: Optional[Text] = None,
        new_item_path: Optional[Text] = None,
        **kwargs: KwargsT
    ) -> None: ...
    moveItem = move_item
    def refresh_item(self, item_path: Optional[Text] = None) -> None: ...
    refreshItem = refresh_item
    def mark_as_read(
        self,
        item_path: Optional[Text] = None,
        article_id: Optional[Text | int] = None,
        **kwargs: KwargsT
    ) -> None: ...
    markAsRead = mark_as_read
    def set_rule(
        self,
        rule_name: Optional[Text] = None,
        rule_def: Optional[Mapping[Text, JsonValueT]] = None,
        **kwargs: KwargsT
    ) -> None: ...
    setRule = set_rule
    def rename_rule(
        self,
        orig_rule_name: Optional[Text] = None,
        new_rule_name: Optional[Text] = None,
        **kwargs: KwargsT
    ) -> None: ...
    renameRule = rename_rule
    def remove_rule(
        self,
        rule_name: Optional[Text] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    removeRule = remove_rule
    @property
    def rules(self) -> RSSRulesDictionary: ...
    def matching_articles(
        self,
        rule_name: Optional[Text] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    matchingArticles = matching_articles

    class _Items(ClientCache):
        def __call__(
            self,
            include_feed_data: Optional[bool] = None,
            **kwargs: KwargsT,
        ) -> RSSitemsDictionary: ...
        @property
        def without_data(self) -> RSSitemsDictionary: ...
        @property
        def with_data(self) -> RSSitemsDictionary: ...

class RSSAPIMixIn(AppAPIMixIn):
    @property
    def rss(self) -> RSS: ...
    def rss_add_folder(
        self,
        folder_path: Optional[Text] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    rss_addFolder = rss_add_folder
    def rss_add_feed(
        self,
        url: Optional[Text] = None,
        item_path: Optional[Text] = None,
        **kwargs: KwargsT
    ) -> None: ...
    rss_addFeed = rss_add_feed
    def rss_remove_item(
        self,
        item_path: Optional[Text] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    rss_removeItem = rss_remove_item
    def rss_move_item(
        self,
        orig_item_path: Optional[Text] = None,
        new_item_path: Optional[Text] = None,
        **kwargs: KwargsT
    ) -> None: ...
    rss_moveItem = rss_move_item
    def rss_items(
        self,
        include_feed_data: Optional[bool] = None,
        **kwargs: KwargsT,
    ) -> RSSitemsDictionary: ...
    def rss_refresh_item(
        self,
        item_path: Optional[Text] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    rss_refreshItem = rss_refresh_item
    def rss_mark_as_read(
        self,
        item_path: Optional[Text] = None,
        article_id: Optional[Text | int] = None,
        **kwargs: KwargsT
    ) -> None: ...
    rss_markAsRead = rss_mark_as_read
    def rss_set_rule(
        self,
        rule_name: Optional[Text] = None,
        rule_def: Optional[Mapping[Text, JsonValueT]] = None,
        **kwargs: KwargsT
    ) -> None: ...
    rss_setRule = rss_set_rule
    def rss_rename_rule(
        self,
        orig_rule_name: Optional[Text] = None,
        new_rule_name: Optional[Text] = None,
        **kwargs: KwargsT
    ) -> None: ...
    rss_renameRule = rss_rename_rule
    def rss_remove_rule(
        self,
        rule_name: Optional[Text] = None,
        **kwargs: KwargsT,
    ) -> None: ...
    rss_removeRule = rss_remove_rule
    def rss_rules(self, **kwargs: KwargsT) -> RSSRulesDictionary: ...
    def rss_matching_articles(
        self,
        rule_name: Optional[Text] = None,
        **kwargs: KwargsT,
    ) -> RSSitemsDictionary: ...
    rss_matchingArticles = rss_matching_articles
