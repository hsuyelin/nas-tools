# Copyright (c) 2018-2022 Trim21 <i@trim21.me>
# Copyright (c) 2008-2014 Erik Svensson <erik.public@gmail.com>
# Licensed under the MIT license.
import enum
import logging
from typing import Dict, Optional, NamedTuple

LOGGER = logging.getLogger("transmission-rpc")
LOGGER.setLevel(logging.ERROR)


def mirror_dict(source: dict) -> dict:
    """
    Creates a dictionary with all values as keys and all keys as values.
    """
    source.update({value: key for key, value in source.items()})
    return source


DEFAULT_TIMEOUT = 30.0


class Priority(enum.IntEnum):
    Low = -1
    Normal = 0
    High = 1


# TODO: remove this in 5.0
TR_PRI_LOW = Priority.Low
TR_PRI_NORMAL = Priority.Normal
TR_PRI_HIGH = Priority.High

PRIORITY = mirror_dict({"low": TR_PRI_LOW, "normal": TR_PRI_NORMAL, "high": TR_PRI_HIGH})

# TODO: remove this in 5.0
TR_RATIOLIMIT_GLOBAL = 0  # follow the global settings
TR_RATIOLIMIT_SINGLE = 1  # override the global settings, seeding until a certain ratio
TR_RATIOLIMIT_UNLIMITED = 2  # override the global settings, seeding regardless of ratio


class RatioLimit(enum.IntEnum):
    Global = TR_RATIOLIMIT_GLOBAL
    Single = TR_RATIOLIMIT_SINGLE
    Unlimited = TR_RATIOLIMIT_UNLIMITED


RATIO_LIMIT = mirror_dict(
    {
        "global": TR_RATIOLIMIT_GLOBAL,
        "single": TR_RATIOLIMIT_SINGLE,
        "unlimited": TR_RATIOLIMIT_UNLIMITED,
    }
)


class IdleLimit(enum.IntEnum):
    Global = 0
    Single = 1
    Unlimited = 2


# TODO: remove this in 5.0
TR_IDLELIMIT_GLOBAL = IdleLimit.Global  # follow the global settings
TR_IDLELIMIT_SINGLE = IdleLimit.Single  # override the global settings, seeding until a certain idle time
TR_IDLELIMIT_UNLIMITED = IdleLimit.Unlimited  # override the global settings, seeding regardless of activity

IDLE_LIMIT = mirror_dict(
    {
        "global": TR_RATIOLIMIT_GLOBAL,
        "single": TR_RATIOLIMIT_SINGLE,
        "unlimited": TR_RATIOLIMIT_UNLIMITED,
    }
)


class Args(NamedTuple):
    type: str
    added_version: int
    removed_version: Optional[int] = None
    previous_argument_name: Optional[str] = None
    next_argument_name: Optional[str] = None
    description: str = ""

    def __repr__(self) -> str:
        return (
            f"Args({self.type!r},"
            f" {self.added_version!r},"
            f" {self.removed_version!r},"
            f" {self.previous_argument_name!r},"
            f" {self.next_argument_name!r},"
            f" {self.description!r})"
        )

    def __str__(self) -> str:
        return f"Args<type={self.type}, {self.added_version}, description={self.description!r})"


class Type:
    number = "number"
    string = "string"
    array = "array"
    boolean = "boolean"
    double = "double"
    object = "object"


trackerListDescription = "A Iterable[Iterable[str]] for a set of announce URLs, each inner list is for a tier"

TORRENT_GET_ARGS: Dict[str, Args] = {
    "activityDate": Args(Type.number, 1, description="Last time of upload or download activity."),
    "addedDate": Args(Type.number, 1, description="The date when this torrent was first added."),
    "bandwidthPriority": Args(Type.number, 5, description="Bandwidth priority. Low (-1), Normal (0) or High (1)."),
    "comment": Args(Type.string, 1, description="Torrent comment."),
    "corruptEver": Args(Type.number, 1, description="Number of bytes of corrupt data downloaded."),
    "creator": Args(Type.string, 1, description="Torrent creator."),
    "dateCreated": Args(Type.number, 1, description="Torrent creation date."),
    "desiredAvailable": Args(Type.number, 1, description="Number of bytes available and left to be downloaded."),
    "doneDate": Args(Type.number, 1, description="The date when the torrent finished downloading."),
    "downloadDir": Args(Type.string, 4, description="The directory path where the torrent is downloaded to."),
    "downloadedEver": Args(Type.number, 1, description="Number of bytes of good data downloaded."),
    "downloadLimit": Args(Type.number, 1, None, None, None, "Download limit in Kbps."),
    "downloadLimitMode": Args(
        Type.number, 1, 5, description="Download limit mode. 0 means global, 1 means single, 2 unlimited."
    ),
    "downloadLimited": Args(Type.boolean, 5, None, None, None, "Download limit is enabled"),
    "editDate": Args(Type.number, 16),
    "error": Args(
        Type.number,
        1,
        description="Kind of error. 0 means OK, 1 means tracker warning, 2 means tracker error, 3 means local error.",
    ),
    "errorString": Args(Type.number, 1, None, None, None, "Error message."),
    "eta": Args(
        Type.number,
        1,
        description="Estimated number of seconds left when downloading or seeding. -1 means not available and -2 means unknown.",
    ),
    "etaIdle": Args(
        Type.number,
        15,
        description="Estimated number of seconds left until the idle time limit is reached. -1 means not available and -2 means unknown.",
    ),
    "files": Args(Type.array, 1, description="Array of file object containing key, bytesCompleted, length and name."),
    "fileStats": Args(
        Type.array, 5, description="Away of file statistics containing bytesCompleted, wanted and priority."
    ),
    "group": Args(Type.string, 17, description="The name of this torrent's bandwidth group"),
    "hashString": Args(Type.string, 1, description="Hashstring unique for the torrent even between sessions."),
    "haveUnchecked": Args(Type.number, 1, None, None, None, "Number of bytes of partial pieces."),
    "haveValid": Args(Type.number, 1, description="Number of bytes of checksum verified data."),
    "honorsSessionLimits": Args(Type.boolean, 5, description="True if session upload limits are honored"),
    "id": Args(Type.number, 1, None, None, None, "Session unique torrent id."),
    "isFinished": Args(Type.boolean, 9, description="True if the torrent is finished. Downloaded and seeded."),
    "isPrivate": Args(Type.boolean, 1, None, None, None, "True if the torrent is private."),
    "isStalled": Args(Type.boolean, 14, description="True if the torrent has stalled (been idle for a long time)."),
    "labels": Args(Type.array, 16, None, None, None, "array of string labels"),
    "leftUntilDone": Args(Type.number, 1, description="Number of bytes left until the download is done."),
    "magnetLink": Args(Type.string, 7, None, None, None, "The magnet link for this torrent."),
    "manualAnnounceTime": Args(Type.number, 1, description="The time until you manually ask for more peers."),
    "maxConnectedPeers": Args(Type.number, 1, None, None, None, "Maximum of connected peers."),
    "metadataPercentComplete": Args(Type.number, 7, description="Download progress of metadata. 0.0 to 1.0."),
    "name": Args(Type.string, 1, None, None, None, "Torrent name."),
    "peer-limit": Args(Type.number, 5, None, None, None, "Maximum number of peers."),
    "peers": Args(Type.array, 2, None, None, None, "Array of peer objects."),
    "peersConnected": Args(Type.number, 1, None, None, None, "Number of peers we are connected to."),
    "peersFrom": Args(Type.object, 1, description="Object containing download peers counts for different peer types."),
    "peersGettingFromUs": Args(Type.number, 1, description="Number of peers we are sending data to."),
    "peersSendingToUs": Args(Type.number, 1, None, None, None, "Number of peers sending to us"),
    "percentComplete": Args(Type.double, 17),
    "percentDone": Args(Type.double, 5, description="Download progress of selected files. 0.0 to 1.0."),
    "pieces": Args(Type.string, 5, description="String with base64 encoded bitfield indicating finished pieces."),
    "pieceCount": Args(Type.number, 1, None, None, None, "Number of pieces."),
    "pieceSize": Args(Type.number, 1, None, None, None, "Number of bytes in a piece."),
    "priorities": Args(Type.array, 1, None, None, None, "Array of file priorities."),
    "primary-mime-type": Args(Type.string, 17),
    "queuePosition": Args(Type.number, 14, None, None, None, "The queue position."),
    "rateDownload": Args(Type.number, 1, None, None, None, "(B/s)"),
    "rateUpload": Args(Type.number, 1, None, None, None, "(B/s)"),
    "recheckProgress": Args(Type.double, 1, None, None, None, "Progress of recheck. 0.0 to 1.0."),
    "secondsDownloading": Args(Type.number, 15, None, None, None, ""),
    "secondsSeeding": Args(Type.number, 15, None, None, None, ""),
    "seedIdleLimit": Args(Type.number, 10, None, None, None, "Idle limit in minutes."),
    "seedIdleMode": Args(Type.number, 10, description="Use global (0), torrent (1), or unlimited (2) limit."),
    "seedRatioLimit": Args(Type.double, 5, None, None, None, "Seed ratio limit."),
    "seedRatioMode": Args(Type.number, 5, description="Use global (0), torrent (1), or unlimited (2) limit."),
    "sizeWhenDone": Args(Type.number, 1, description="Size of the torrent download in bytes."),
    "startDate": Args(Type.number, 1, description="The date when the torrent was last started."),
    "status": Args(Type.number, 1, None, None, None, "Current status, see source"),
    "trackers": Args(Type.array, 1, None, None, None, "Array of tracker objects."),
    "trackerStats": Args(Type.object, 7, description="Array of object containing tracker statistics."),
    "totalSize": Args(Type.number, 1, None, None, None, "Total size of the torrent in bytes"),
    "torrentFile": Args(Type.string, 5, None, None, None, "Path to .torrent file."),
    "uploadedEver": Args(Type.number, 1, None, None, None, "Number of bytes uploaded, ever."),
    "uploadLimit": Args(Type.number, 1, None, None, None, "Upload limit in Kbps"),
    "uploadLimited": Args(Type.boolean, 5, None, None, None, "Upload limit enabled."),
    "uploadRatio": Args(Type.double, 1, None, None, None, "Seed ratio."),
    "wanted": Args(Type.array, 1, description="Array of booleans indicated wanted files."),
    "webseeds": Args(Type.array, 1, None, None, None, "Array of webseeds objects"),
    "webseedsSendingToUs": Args(Type.number, 1, None, None, None, "Number of webseeds seeding to us."),
    "file-count": Args(Type.number, 17),
    "trackerList": Args(Type.array, 17, description=trackerListDescription),
}


class RpcMethod(str, enum.Enum):
    SessionSet = "session-set"
    SessionGet = "session-get"
    SessionStats = "session-stats"

    TorrentGet = "torrent-get"
    TorrentAdd = "torrent-add"
    TorrentSet = "torrent-set"
    TorrentRemove = "torrent-remove"

    TorrentStart = "torrent-start"
    TorrentStartNow = "torrent-start-now"
    TorrentStop = "torrent-stop"

    TorrentVerify = "torrent-verify"
    TorrentReannounce = "torrent-reannounce"

    TorrentSetLocation = "torrent-set-location"
    TorrentRenamePath = "torrent-rename-path"

    QueueMoveTop = "queue-move-top"
    QueueMoveBottom = "queue-move-bottom"
    QueueMoveUp = "queue-move-up"
    QueueMoveDown = "queue-move-down"

    GroupSet = "group-set"
    GroupGet = "group-get"

    FreeSpace = "free-space"

    PortTest = "port-test"

    BlocklistUpdate = "blocklist-update"
