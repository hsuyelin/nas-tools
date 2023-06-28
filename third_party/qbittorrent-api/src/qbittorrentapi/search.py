from qbittorrentapi.app import AppAPIMixIn
from qbittorrentapi.decorators import alias
from qbittorrentapi.decorators import aliased
from qbittorrentapi.decorators import endpoint_introduced
from qbittorrentapi.decorators import login_required
from qbittorrentapi.decorators import version_removed
from qbittorrentapi.definitions import APINames
from qbittorrentapi.definitions import ClientCache
from qbittorrentapi.definitions import Dictionary
from qbittorrentapi.definitions import List
from qbittorrentapi.definitions import ListEntry


class SearchJobDictionary(Dictionary):
    """Response for :meth:`~SearchAPIMixIn.search_start`"""

    def __init__(self, data, client):
        self._search_job_id = data.get("id", None)
        super(SearchJobDictionary, self).__init__(data=data, client=client)

    def stop(self, **kwargs):
        """Implements :meth:`~SearchAPIMixIn.search_stop`"""
        return self._client.search_stop(search_id=self._search_job_id, **kwargs)

    def status(self, **kwargs):
        """Implements :meth:`~SearchAPIMixIn.search_status`"""
        return self._client.search_status(search_id=self._search_job_id, **kwargs)

    def results(self, limit=None, offset=None, **kwargs):
        """Implements :meth:`~SearchAPIMixIn.search_results`"""
        return self._client.search_results(
            limit=limit, offset=offset, search_id=self._search_job_id, **kwargs
        )

    def delete(self, **kwargs):
        """Implements :meth:`~SearchAPIMixIn.search_delete`"""
        return self._client.search_delete(search_id=self._search_job_id, **kwargs)


class SearchResultsDictionary(Dictionary):
    """Response for :meth:`~SearchAPIMixIn.search_results`"""


class SearchStatusesList(List):
    """Response for :meth:`~SearchAPIMixIn.search_status`"""

    def __init__(self, list_entries, client):
        super(SearchStatusesList, self).__init__(
            client=client, entry_class=SearchStatus, list_entries=list_entries
        )


class SearchStatus(ListEntry):
    """Item in :class:`SearchStatusesList`"""


class SearchCategoriesList(List):
    """Response for :meth:`~SearchAPIMixIn.search_categories`"""

    def __init__(self, list_entries, client):
        super(SearchCategoriesList, self).__init__(
            client=client, entry_class=SearchCategory, list_entries=list_entries
        )


class SearchCategory(ListEntry):
    """Item in :class:`SearchCategoriesList`"""


class SearchPluginsList(List):
    """Response for :meth:`~SearchAPIMixIn.search_plugins`"""

    def __init__(self, list_entries, client):
        super(SearchPluginsList, self).__init__(
            client=client, entry_class=SearchPlugin, list_entries=list_entries
        )


class SearchPlugin(ListEntry):
    """Item in :class:`SearchPluginsList`"""


@aliased
class Search(ClientCache):
    """
    Allows interaction with ``Search`` API endpoints.

    :Usage:
        >>> from qbittorrentapi import Client
        >>> client = Client(host='localhost:8080', username='admin', password='adminadmin')
        >>> # this is all the same attributes that are available as named in the
        >>> #  endpoints or the more pythonic names in Client (with or without 'search_' prepended)
        >>> # initiate searches and retrieve results
        >>> search_job = client.search.start(pattern='Ubuntu', plugins='all', category='all')
        >>> status = search_job.status()
        >>> results = search_job.result()
        >>> search_job.delete()
        >>> # inspect and manage plugins
        >>> plugins = client.search.plugins
        >>> cats = client.search.categories(plugin_name='...')
        >>> client.search.install_plugin(sources='...')
        >>> client.search.update_plugins()
    """

    def start(self, pattern=None, plugins=None, category=None, **kwargs):
        """Implements :meth:`~SearchAPIMixIn.search_start`"""
        return self._client.search_start(
            pattern=pattern, plugins=plugins, category=category, **kwargs
        )

    def stop(self, search_id=None, **kwargs):
        """Implements :meth:`~SearchAPIMixIn.search_stop`"""
        return self._client.search_stop(search_id=search_id, **kwargs)

    def status(self, search_id=None, **kwargs):
        """Implements :meth:`~SearchAPIMixIn.search_status`"""
        return self._client.search_status(search_id=search_id, **kwargs)

    def results(self, search_id=None, limit=None, offset=None, **kwargs):
        """Implements :meth:`~SearchAPIMixIn.search_results`"""
        return self._client.search_results(
            search_id=search_id, limit=limit, offset=offset, **kwargs
        )

    def delete(self, search_id=None, **kwargs):
        """Implements :meth:`~SearchAPIMixIn.search_delete`"""
        return self._client.search_delete(search_id=search_id, **kwargs)

    def categories(self, plugin_name=None, **kwargs):
        """Implements :meth:`~SearchAPIMixIn.search_categories`"""
        return self._client.search_categories(plugin_name=plugin_name, **kwargs)

    @property
    def plugins(self):
        """Implements :meth:`~SearchAPIMixIn.search_plugins`"""
        return self._client.search_plugins()

    @alias("installPlugin")
    def install_plugin(self, sources=None, **kwargs):
        """Implements :meth:`~SearchAPIMixIn.search_install_plugin`"""
        return self._client.search_install_plugin(sources=sources, **kwargs)

    @alias("uninstallPlugin")
    def uninstall_plugin(self, sources=None, **kwargs):
        """Implements :meth:`~SearchAPIMixIn.search_uninstall_plugin`"""
        return self._client.search_uninstall_plugin(sources=sources, **kwargs)

    @alias("enablePlugin")
    def enable_plugin(self, plugins=None, enable=None, **kwargs):
        """Implements :meth:`~SearchAPIMixIn.search_enable_plugin`"""
        return self._client.search_enable_plugin(
            plugins=plugins, enable=enable, **kwargs
        )

    @alias("updatePlugins")
    def update_plugins(self, **kwargs):
        """Implements :meth:`~SearchAPIMixIn.search_update_plugins`"""
        return self._client.search_update_plugins(**kwargs)


@aliased
class SearchAPIMixIn(AppAPIMixIn):
    """
    Implementation for all ``Search`` API methods.

    :Usage:
        >>> from qbittorrentapi import Client
        >>> client = Client(host='localhost:8080', username='admin', password='adminadmin')
        >>> search_job = client.search_start(pattern='Ubuntu', plugins='all', category='all')
        >>> client.search_stop(search_id=search_job.id)
        >>> # or
        >>> search_job.stop()
        >>>
    """

    @property
    def search(self):
        """
        Allows for transparent interaction with ``Search`` endpoints.

        See Search class for usage.
        :return: Search object
        """
        if self._search is None:
            self._search = Search(client=self)
        return self._search

    @endpoint_introduced("2.1.1", "search/start")
    @login_required
    def search_start(self, pattern=None, plugins=None, category=None, **kwargs):
        """
        Start a search. Python must be installed. Host may limit number of
        concurrent searches.

        :raises Conflict409Error:

        :param pattern: term to search for
        :param plugins: list of plugins to use for searching (supports 'all' and 'enabled')
        :param category: categories to limit search; dependent on plugins. (supports 'all')
        :return: :class:`SearchJobDictionary`
        """
        data = {
            "pattern": pattern,
            "plugins": self._list2string(plugins, "|"),
            "category": category,
        }
        return self._post(
            _name=APINames.Search,
            _method="start",
            data=data,
            response_class=SearchJobDictionary,
            **kwargs
        )

    @endpoint_introduced("2.1.1", "search/stop")
    @login_required
    def search_stop(self, search_id=None, **kwargs):
        """
        Stop a running search.

        :raises NotFound404Error:

        :param search_id: ID of search job to stop
        :return: None
        """
        data = {"id": search_id}
        self._post(_name=APINames.Search, _method="stop", data=data, **kwargs)

    @endpoint_introduced("2.1.1", "search/status")
    @login_required
    def search_status(self, search_id=None, **kwargs):
        """
        Retrieve status of one or all searches.

        :raises NotFound404Error:

        :param search_id: ID of search to get status; leave emtpy for status of all jobs
        :return: :class:`SearchStatusesList` - `<https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)#get-search-status>`_
        """  # noqa: E501
        params = {"id": search_id}
        return self._get(
            _name=APINames.Search,
            _method="status",
            params=params,
            response_class=SearchStatusesList,
            **kwargs
        )

    @endpoint_introduced("2.1.1", "search/results")
    @login_required
    def search_results(self, search_id=None, limit=None, offset=None, **kwargs):
        """
        Retrieve the results for the search.

        :raises NotFound404Error:
        :raises Conflict409Error:

        :param search_id: ID of search job
        :param limit: number of results to return
        :param offset: where to start returning results
        :return: :class:`SearchResultsDictionary` - `<https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)#get-search-results>`_
        """  # noqa: E501
        data = {"id": search_id, "limit": limit, "offset": offset}
        return self._post(
            _name=APINames.Search,
            _method="results",
            data=data,
            response_class=SearchResultsDictionary,
            **kwargs
        )

    @endpoint_introduced("2.1.1", "search/delete")
    @login_required
    def search_delete(self, search_id=None, **kwargs):
        """
        Delete a search job.

        :raises NotFound404Error:

        :param search_id: ID of search to delete
        :return: None
        """
        data = {"id": search_id}
        self._post(_name=APINames.Search, _method="delete", data=data, **kwargs)

    @endpoint_introduced("2.1.1", "search/categories")
    @version_removed("2.6", "search/categories")
    @login_required
    def search_categories(self, plugin_name=None, **kwargs):
        """
        Retrieve categories for search.

        Note: endpoint was removed in qBittorrent v4.3.0

        :param plugin_name: Limit categories returned by plugin(s) (supports ``all`` and ``enabled``)
        :return: :class:`SearchCategoriesList`
        """
        data = {"pluginName": plugin_name}
        return self._post(
            _name=APINames.Search,
            _method="categories",
            data=data,
            response_class=SearchCategoriesList,
            **kwargs
        )

    @endpoint_introduced("2.1.1", "search/plugins")
    @login_required
    def search_plugins(self, **kwargs):
        """
        Retrieve details of search plugins.

        :return: :class:`SearchPluginsList` - `<https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)#get-search-plugins>`_
        """  # noqa: E501
        return self._get(
            _name=APINames.Search,
            _method="plugins",
            response_class=SearchPluginsList,
            **kwargs
        )

    @endpoint_introduced("2.1.1", "search/installPlugin")
    @alias("search_installPlugin")
    @login_required
    def search_install_plugin(self, sources=None, **kwargs):
        """
        Install search plugins from either URL or file.

        :param sources: list of URLs or filepaths
        :return: None
        """
        data = {"sources": self._list2string(sources, "|")}
        self._post(_name=APINames.Search, _method="installPlugin", data=data, **kwargs)

    @endpoint_introduced("2.1.1", "search/uninstallPlugin")
    @alias("search_uninstallPlugin")
    @login_required
    def search_uninstall_plugin(self, names=None, **kwargs):
        """
        Uninstall search plugins.

        :param names: names of plugins to uninstall
        :return: None
        """
        data = {"names": self._list2string(names, "|")}
        self._post(
            _name=APINames.Search, _method="uninstallPlugin", data=data, **kwargs
        )

    @endpoint_introduced("2.1.1", "search/enablePlugin")
    @alias("search_enablePlugin")
    @login_required
    def search_enable_plugin(self, plugins=None, enable=None, **kwargs):
        """
        Enable or disable search plugin(s).

        :param plugins: list of plugin names
        :param enable: True or False
        :return: None
        """
        data = {"names": self._list2string(plugins, "|"), "enable": enable}
        self._post(_name=APINames.Search, _method="enablePlugin", data=data, **kwargs)

    @endpoint_introduced("2.1.1", "search/updatePlugin")
    @alias("search_updatePlugins")
    @login_required
    def search_update_plugins(self, **kwargs):
        """
        Auto update search plugins.

        :return: None
        """
        self._post(_name=APINames.Search, _method="updatePlugins", **kwargs)
