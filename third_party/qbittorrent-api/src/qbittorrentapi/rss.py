from json import dumps

from qbittorrentapi._version_support import v
from qbittorrentapi.app import AppAPIMixIn
from qbittorrentapi.decorators import alias
from qbittorrentapi.decorators import aliased
from qbittorrentapi.decorators import endpoint_introduced
from qbittorrentapi.decorators import login_required
from qbittorrentapi.definitions import APINames
from qbittorrentapi.definitions import ClientCache
from qbittorrentapi.definitions import Dictionary


class RSSitemsDictionary(Dictionary):
    """Response for :meth:`~RSSAPIMixIn.rss_items`"""


class RSSRulesDictionary(Dictionary):
    """Response for :meth:`~RSSAPIMixIn.rss_rules`"""


@aliased
class RSS(ClientCache):
    """
    Allows interaction with ``RSS`` API endpoints.

    :Usage:
        >>> from qbittorrentapi import Client
        >>> client = Client(host='localhost:8080', username='admin', password='adminadmin')
        >>> # this is all the same attributes that are available as named in the
        >>> #  endpoints or the more pythonic names in Client (with or without 'log_' prepended)
        >>> rss_rules = client.rss.rules
        >>> client.rss.addFolder(folder_path="TPB")
        >>> client.rss.addFeed(url='...', item_path="TPB\\Top100")
        >>> client.rss.remove_item(item_path="TPB") # deletes TPB and Top100
        >>> client.rss.set_rule(rule_name="...", rule_def={...})
        >>> items = client.rss.items.with_data
        >>> items_no_data = client.rss.items.without_data
    """

    def __init__(self, client):
        super(RSS, self).__init__(client=client)
        self.items = RSS._Items(client=client)

    @alias("addFolder")
    def add_folder(self, folder_path=None, **kwargs):
        """Implements :meth:`~RSSAPIMixIn.rss_add_folder`"""
        return self._client.rss_add_folder(folder_path=folder_path, **kwargs)

    @alias("addFeed")
    def add_feed(self, url=None, item_path=None, **kwargs):
        """Implements :meth:`~RSSAPIMixIn.rss_add_feed`"""
        return self._client.rss_add_feed(url=url, item_path=item_path, **kwargs)

    @alias("removeItem")
    def remove_item(self, item_path=None, **kwargs):
        """Implements :meth:`~RSSAPIMixIn.rss_remove_item`"""
        return self._client.rss_remove_item(item_path=item_path, **kwargs)

    @alias("moveItem")
    def move_item(self, orig_item_path=None, new_item_path=None, **kwargs):
        """Implements :meth:`~RSSAPIMixIn.rss_move_item`"""
        return self._client.rss_move_item(
            orig_item_path=orig_item_path, new_item_path=new_item_path, **kwargs
        )

    @alias("refreshItem")
    def refresh_item(self, item_path=None):
        """Implements :meth:`~RSSAPIMixIn.rss_refresh_item`"""
        return self._client.rss_refresh_item(item_path=item_path)

    @alias("markAsRead")
    def mark_as_read(self, item_path=None, article_id=None, **kwargs):
        """Implements :meth:`~RSSAPIMixIn.rss_mark_as_read`"""
        return self._client.rss_mark_as_read(
            item_path=item_path, article_id=article_id, **kwargs
        )

    @alias("setRule")
    def set_rule(self, rule_name=None, rule_def=None, **kwargs):
        """Implements :meth:`~RSSAPIMixIn.rss_set_rule`"""
        return self._client.rss_set_rule(
            rule_name=rule_name, rule_def=rule_def, **kwargs
        )

    @alias("renameRule")
    def rename_rule(self, orig_rule_name=None, new_rule_name=None, **kwargs):
        """Implements :meth:`~RSSAPIMixIn.rss_rename_rule`"""
        return self._client.rss_rename_rule(
            orig_rule_name=orig_rule_name, new_rule_name=new_rule_name, **kwargs
        )

    @alias("removeRule")
    def remove_rule(self, rule_name=None, **kwargs):
        """Implements :meth:`~RSSAPIMixIn.rss_remove_rule`"""
        return self._client.rss_remove_rule(rule_name=rule_name, **kwargs)

    @property
    def rules(self):
        """Implements :meth:`~RSSAPIMixIn.rss_rules`"""
        return self._client.rss_rules()

    @alias("matchingArticles")
    def matching_articles(self, rule_name=None, **kwargs):
        """Implements :meth:`~RSSAPIMixIn.rss_matching_articles`"""
        return self._client.rss_matching_articles(rule_name=rule_name, **kwargs)

    class _Items(ClientCache):
        def __call__(self, include_feed_data=None, **kwargs):
            return self._client.rss_items(include_feed_data=include_feed_data, **kwargs)

        @property
        def without_data(self):
            return self._client.rss_items(include_feed_data=False)

        @property
        def with_data(self):
            return self._client.rss_items(include_feed_data=True)


@aliased
class RSSAPIMixIn(AppAPIMixIn):
    """
    Implementation of all ``RSS`` API methods.

    :Usage:
        >>> from qbittorrentapi import Client
        >>> client = Client(host='localhost:8080', username='admin', password='adminadmin')
        >>> rss_rules = client.rss_rules()
        >>> client.rss_set_rule(rule_name="...", rule_def={...})
    """

    @property
    def rss(self):
        """
        Allows for transparent interaction with RSS endpoints.

        See RSS class for usage.
        :return: RSS object
        """
        if self._rss is None:
            self._rss = RSS(client=self)
        return self._rss

    @alias("rss_addFolder")
    @login_required
    def rss_add_folder(self, folder_path=None, **kwargs):
        """
        Add an RSS folder. Any intermediate folders in path must already exist.

        :raises Conflict409Error:

        :param folder_path: path to new folder (e.g. ``Linux\\ISOs``)
        :return: None
        """
        data = {"path": folder_path}
        self._post(_name=APINames.RSS, _method="addFolder", data=data, **kwargs)

    @alias("rss_addFeed")
    @login_required
    def rss_add_feed(self, url=None, item_path=None, **kwargs):
        """
        Add new RSS feed. Folders in path must already exist.

        :raises Conflict409Error:

        :param url: URL of RSS feed (e.g https://distrowatch.com/news/torrents.xml)
        :param item_path: Name and/or path for new feed (e.g. ``Folder\\Subfolder\\FeedName``)
        :return: None
        """
        data = {"url": url, "path": item_path}
        self._post(_name=APINames.RSS, _method="addFeed", data=data, **kwargs)

    @alias("rss_removeItem")
    @login_required
    def rss_remove_item(self, item_path=None, **kwargs):
        """
        Remove an RSS item (folder, feed, etc).

        NOTE: Removing a folder also removes everything in it.

        :raises Conflict409Error:

        :param item_path: path to item to be removed (e.g. ``Folder\\Subfolder\\ItemName``)
        :return: None
        """
        data = {"path": item_path}
        self._post(_name=APINames.RSS, _method="removeItem", data=data, **kwargs)

    @alias("rss_moveItem")
    @login_required
    def rss_move_item(self, orig_item_path=None, new_item_path=None, **kwargs):
        """
        Move/rename an RSS item (folder, feed, etc).

        :raises Conflict409Error:

        :param orig_item_path: path to item to be removed (e.g. ``Folder\\Subfolder\\ItemName``)
        :param new_item_path: path to item to be removed (e.g. ``Folder\\Subfolder\\ItemName``)
        :return: None
        """
        data = {"itemPath": orig_item_path, "destPath": new_item_path}
        self._post(_name=APINames.RSS, _method="moveItem", data=data, **kwargs)

    @login_required
    def rss_items(self, include_feed_data=None, **kwargs):
        """
        Retrieve RSS items and optionally feed data.

        :param include_feed_data: True or false to include feed data
        :return: :class:`RSSitemsDictionary`
        """
        params = {"withData": include_feed_data}
        return self._get(
            _name=APINames.RSS,
            _method="items",
            params=params,
            response_class=RSSitemsDictionary,
            **kwargs
        )

    @endpoint_introduced("2.2", "rss/refreshItem")
    @alias("rss_refreshItem")
    @login_required
    def rss_refresh_item(self, item_path=None, **kwargs):
        """
        Trigger a refresh for an RSS item.

        :param item_path: path to item to be refreshed (e.g. ``Folder\\Subfolder\\ItemName``)
        :return: None
        """
        # HACK: v4.1.7 and v4.1.8 both use api v2.2; however, refreshItem was introduced in v4.1.8
        if v(self.app_version()) > v("v4.1.7"):
            data = {"itemPath": item_path}
            self._post(_name=APINames.RSS, _method="refreshItem", data=data, **kwargs)

    @endpoint_introduced("2.5.1", "rss/markAsRead")
    @alias("rss_markAsRead")
    @login_required
    def rss_mark_as_read(self, item_path=None, article_id=None, **kwargs):
        """
        Mark RSS article as read. If article ID is not provider, the entire
        feed is marked as read.

        :raises NotFound404Error:

        :param item_path: path to item to be refreshed (e.g. ``Folder\\Subfolder\\ItemName``)
        :param article_id: article ID from :meth:`~RSSAPIMixIn.rss_items`
        :return: None
        """
        data = {"itemPath": item_path, "articleId": article_id}
        self._post(_name=APINames.RSS, _method="markAsRead", data=data, **kwargs)

    @alias("rss_setRule")
    @login_required
    def rss_set_rule(self, rule_name=None, rule_def=None, **kwargs):
        """
        Create a new RSS auto-downloading rule.

        :param rule_name: name for new rule
        :param rule_def: dictionary with rule fields - `<https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)#set-auto-downloading-rule>`_
        :return: None
        """  # noqa: E501
        data = {"ruleName": rule_name, "ruleDef": dumps(rule_def)}
        self._post(_name=APINames.RSS, _method="setRule", data=data, **kwargs)

    @alias("rss_renameRule")
    @login_required
    def rss_rename_rule(self, orig_rule_name=None, new_rule_name=None, **kwargs):
        """
        Rename an RSS auto-download rule.

        Note: this endpoint did not work properly until qBittorrent v4.3.0

        :param orig_rule_name: current name of rule
        :param new_rule_name: new name for rule
        :return: None
        """
        data = {"ruleName": orig_rule_name, "newRuleName": new_rule_name}
        self._post(_name=APINames.RSS, _method="renameRule", data=data, **kwargs)

    @alias("rss_removeRule")
    @login_required
    def rss_remove_rule(self, rule_name=None, **kwargs):
        """
        Delete a RSS auto-downloading rule.

        :param rule_name: Name of rule to delete
        :return: None
        """
        data = {"ruleName": rule_name}
        self._post(_name=APINames.RSS, _method="removeRule", data=data, **kwargs)

    @login_required
    def rss_rules(self, **kwargs):
        """
        Retrieve RSS auto-download rule definitions.

        :return: :class:`RSSRulesDictionary`
        """
        return self._get(
            _name=APINames.RSS,
            _method="rules",
            response_class=RSSRulesDictionary,
            **kwargs
        )

    @endpoint_introduced("2.5.1", "rss/matchingArticles")
    @alias("rss_matchingArticles")
    @login_required
    def rss_matching_articles(self, rule_name=None, **kwargs):
        """
        Fetch all articles matching a rule.

        :param rule_name: Name of rule to return matching articles
        :return: :class:`RSSitemsDictionary`
        """
        data = {"ruleName": rule_name}
        return self._post(
            _name=APINames.RSS,
            _method="matchingArticles",
            data=data,
            response_class=RSSitemsDictionary,
            **kwargs
        )
