from enum import Enum

try:
    from collections import UserList
except ImportError:  # pragma: no cover
    from UserList import UserList

from qbittorrentapi._attrdict import AttrDict


class APINames(Enum):
    """
    API namespaces for API endpoints.

    e.g ``torrents`` in ``http://localhost:8080/api/v2/torrents/addTrackers``
    """

    Authorization = "auth"
    Application = "app"
    Log = "log"
    Sync = "sync"
    Transfer = "transfer"
    Torrents = "torrents"
    RSS = "rss"
    Search = "search"
    EMPTY = ""


class TorrentState(Enum):
    """
    Torrent States as defined by qBittorrent.

    Definitions:
        - wiki: `<https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)#get-torrent-list>`_
        - code: `<https://github.com/qbittorrent/qBittorrent/blob/5dcc14153f046209f1067299494a82e5294d883a/src/base/bittorrent/torrent.h#L73>`_

    :Usage:
        >>> from qbittorrentapi import Client, TorrentState
        >>> client = Client()
        >>> # print torrent hashes for torrents that are downloading
        >>> for torrent in client.torrents_info():
        >>>     # check if torrent is downloading
        >>>     if torrent.state_enum.is_downloading:
        >>>         print(f'{torrent.hash} is downloading...')
        >>>     # the appropriate enum member can be directly derived
        >>>     state_enum = TorrentState(torrent.state)
        >>>     print(f'{torrent.hash}: {state_enum.value}')
    """

    ERROR = "error"
    MISSING_FILES = "missingFiles"
    UPLOADING = "uploading"
    PAUSED_UPLOAD = "pausedUP"
    QUEUED_UPLOAD = "queuedUP"
    STALLED_UPLOAD = "stalledUP"
    CHECKING_UPLOAD = "checkingUP"
    FORCED_UPLOAD = "forcedUP"
    ALLOCATING = "allocating"
    DOWNLOADING = "downloading"
    METADATA_DOWNLOAD = "metaDL"
    FORCED_METADATA_DOWNLOAD = "forcedMetaDL"
    PAUSED_DOWNLOAD = "pausedDL"
    QUEUED_DOWNLOAD = "queuedDL"
    FORCED_DOWNLOAD = "forcedDL"
    STALLED_DOWNLOAD = "stalledDL"
    CHECKING_DOWNLOAD = "checkingDL"
    CHECKING_RESUME_DATA = "checkingResumeData"
    MOVING = "moving"
    UNKNOWN = "unknown"

    @property
    def is_downloading(self):
        """Returns ``True`` if the State is categorized as Downloading."""
        return self in {
            TorrentState.DOWNLOADING,
            TorrentState.METADATA_DOWNLOAD,
            TorrentState.FORCED_METADATA_DOWNLOAD,
            TorrentState.STALLED_DOWNLOAD,
            TorrentState.CHECKING_DOWNLOAD,
            TorrentState.PAUSED_DOWNLOAD,
            TorrentState.QUEUED_DOWNLOAD,
            TorrentState.FORCED_DOWNLOAD,
        }

    @property
    def is_uploading(self):
        """Returns ``True`` if the State is categorized as Uploading."""
        return self in {
            TorrentState.UPLOADING,
            TorrentState.STALLED_UPLOAD,
            TorrentState.CHECKING_UPLOAD,
            TorrentState.QUEUED_UPLOAD,
            TorrentState.FORCED_UPLOAD,
        }

    @property
    def is_complete(self):
        """Returns ``True`` if the State is categorized as Complete."""
        return self in {
            TorrentState.UPLOADING,
            TorrentState.STALLED_UPLOAD,
            TorrentState.CHECKING_UPLOAD,
            TorrentState.PAUSED_UPLOAD,
            TorrentState.QUEUED_UPLOAD,
            TorrentState.FORCED_UPLOAD,
        }

    @property
    def is_checking(self):
        """Returns ``True`` if the State is categorized as Checking."""
        return self in {
            TorrentState.CHECKING_UPLOAD,
            TorrentState.CHECKING_DOWNLOAD,
            TorrentState.CHECKING_RESUME_DATA,
        }

    @property
    def is_errored(self):
        """Returns ``True`` if the State is categorized as Errored."""
        return self in {TorrentState.MISSING_FILES, TorrentState.ERROR}

    @property
    def is_paused(self):
        """Returns ``True`` if the State is categorized as Paused."""
        return self in {TorrentState.PAUSED_UPLOAD, TorrentState.PAUSED_DOWNLOAD}


TorrentStates = TorrentState


class TrackerStatus(Enum):
    """
    Tracker Statuses as defined by qBittorrent.

    Definitions:
        - wiki: `<https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)#get-torrent-trackers>`_
        - code: `<https://github.com/qbittorrent/qBittorrent/blob/5dcc14153f046209f1067299494a82e5294d883a/src/base/bittorrent/trackerentry.h#L42>`_

    :Usage:
        >>> from qbittorrentapi import Client, TrackerStatus
        >>> client = Client()
        >>> # print torrent hashes for torrents that are downloading
        >>> for torrent in client.torrents_info():
        >>>     for tracker in torrent.trackers:
        >>>         # display status for each tracker
        >>>         print(f"{torrent.hash[-6:]}: {TrackerStatus(tracker.status).display:>13} :{tracker.url}")
    """

    DISABLED = 0
    NOT_CONTACTED = 1
    WORKING = 2
    UPDATING = 3
    NOT_WORKING = 4

    @property
    def display(self):
        """Returns a descriptive display value for status."""
        return {
            TrackerStatus.DISABLED: "Disabled",
            TrackerStatus.NOT_CONTACTED: "Not contacted",
            TrackerStatus.WORKING: "Working",
            TrackerStatus.UPDATING: "Updating",
            TrackerStatus.NOT_WORKING: "Not working",
        }[self]


class ClientCache(object):
    """
    Caches the client.

    Subclass this for any object that needs access to the Client.
    """

    def __init__(self, *args, **kwargs):
        self._client = kwargs.pop("client")
        super(ClientCache, self).__init__(*args, **kwargs)


class Dictionary(ClientCache, AttrDict):
    """Base definition of dictionary-like objects returned from qBittorrent."""

    def __init__(self, data=None, client=None):
        super(Dictionary, self).__init__(self._normalize(data or {}), client=client)
        # allows updating properties that aren't necessarily a part of the AttrDict
        self._setattr("_allow_invalid_attributes", True)

    @classmethod
    def _normalize(cls, data):
        """Iterate through a dict converting any nested dicts to AttrDicts."""
        if isinstance(data, dict):
            return AttrDict({key: cls._normalize(value) for key, value in data.items()})
        return data


class List(ClientCache, UserList):
    """Base definition for list-like objects returned from qBittorrent."""

    def __init__(self, list_entries=None, entry_class=None, client=None):
        super(List, self).__init__(
            [
                entry_class(data=entry, client=client)
                if isinstance(entry, dict)
                else entry
                for entry in list_entries or ()
            ],
            client=client,
        )


class ListEntry(Dictionary):
    """Base definition for objects within a list returned from qBittorrent."""
