from qbittorrentapi.app import AppAPIMixIn
from qbittorrentapi.decorators import login_required
from qbittorrentapi.definitions import APINames
from qbittorrentapi.definitions import ClientCache
from qbittorrentapi.definitions import List
from qbittorrentapi.definitions import ListEntry


class LogPeersList(List):
    """Response for :meth:`~LogAPIMixIn.log_peers`"""

    def __init__(self, list_entries, client):
        super(LogPeersList, self).__init__(
            client=client, entry_class=LogPeer, list_entries=list_entries
        )


class LogPeer(ListEntry):
    """Item in :class:`LogPeersList`"""


class LogMainList(List):
    """Response to :meth:`~LogAPIMixIn.log_main`"""

    def __init__(self, list_entries, client):
        super(LogMainList, self).__init__(
            client=client, entry_class=LogEntry, list_entries=list_entries
        )


class LogEntry(ListEntry):
    """Item in :class:`LogMainList`"""


class Log(ClientCache):
    """
    Allows interaction with ``Log`` API endpoints.

    :Usage:
        >>> from qbittorrentapi import Client
        >>> client = Client(host='localhost:8080', username='admin', password='adminadmin')
        >>> # this is all the same attributes that are available as named in the
        >>> #  endpoints or the more pythonic names in Client (with or without 'log_' prepended)
        >>> log_list = client.log.main()
        >>> peers_list = client.log.peers(hash='...')
        >>> # can also filter log down with additional attributes
        >>> log_info = client.log.main.info(last_known_id='...')
        >>> log_warning = client.log.main.warning(last_known_id='...')
    """

    def __init__(self, client):
        super(Log, self).__init__(client=client)
        self.main = Log._Main(client=client)

    def peers(self, last_known_id=None, **kwargs):
        """Implements :meth:`~LogAPIMixIn.log_peers`"""
        return self._client.log_peers(last_known_id=last_known_id, **kwargs)

    class _Main(ClientCache):
        def _api_call(
            self,
            normal=None,
            info=None,
            warning=None,
            critical=None,
            last_known_id=None,
            **kwargs
        ):
            return self._client.log_main(
                normal=normal,
                info=info,
                warning=warning,
                critical=critical,
                last_known_id=last_known_id,
                **kwargs
            )

        def __call__(
            self,
            normal=None,
            info=None,
            warning=None,
            critical=None,
            last_known_id=None,
            **kwargs
        ):
            return self._api_call(
                normal=normal,
                info=info,
                warning=warning,
                critial=critical,
                last_known_id=last_known_id,
                **kwargs
            )

        def info(self, last_known_id=None, **kwargs):
            return self._api_call(last_known_id=last_known_id, **kwargs)

        def normal(self, last_known_id=None, **kwargs):
            return self._api_call(info=False, last_known_id=last_known_id, **kwargs)

        def warning(self, last_known_id=None, **kwargs):
            return self._api_call(
                info=False, normal=False, last_known_id=last_known_id, **kwargs
            )

        def critical(self, last_known_id=None, **kwargs):
            return self._api_call(
                info=False,
                normal=False,
                warning=False,
                last_known_id=last_known_id,
                **kwargs
            )


class LogAPIMixIn(AppAPIMixIn):
    """
    Implementation of all ``Log`` API methods.

    :Usage:
        >>> from qbittorrentapi import Client
        >>> client = Client(host='localhost:8080', username='admin', password='adminadmin')
        >>> client.log_main(info=False)
        >>> client.log_peers()
    """

    @property
    def log(self):
        """
        Allows for transparent interaction with Log endpoints.

        See Log class for usage.
        :return: Log object
        """
        if self._log is None:
            self._log = Log(client=self)
        return self._log

    @login_required
    def log_main(
        self,
        normal=None,
        info=None,
        warning=None,
        critical=None,
        last_known_id=None,
        **kwargs
    ):
        """
        Retrieve the qBittorrent log entries. Iterate over returned object.

        :param normal: False to exclude ``normal`` entries
        :param info: False to exclude ``info`` entries
        :param warning: False to exclude ``warning`` entries
        :param critical: False to exclude ``critical`` entries
        :param last_known_id: only entries with an ID greater than this value will be returned
        :return: :class:`LogMainList`
        """
        parameters = {
            "normal": normal,
            "info": info,
            "warning": warning,
            "critical": critical,
            "last_known_id": last_known_id,
        }
        return self._get(
            _name=APINames.Log,
            _method="main",
            params=parameters,
            response_class=LogMainList,
            **kwargs
        )

    @login_required
    def log_peers(self, last_known_id=None, **kwargs):
        """
        Retrieve qBittorrent peer log.

        :param last_known_id: only entries with an ID greater than this value will be returned
        :return: :class:`LogPeersList`
        """
        parameters = {"last_known_id": last_known_id}
        return self._get(
            _name=APINames.Log,
            _method="peers",
            params=parameters,
            response_class=LogPeersList,
            **kwargs
        )
