import warnings
from typing import List, Optional

from typing_extensions import Literal

from transmission_rpc.types import Container


class Stats(Container):
    @property
    def uploaded_bytes(self) -> int:
        return self.fields["uploadedBytes"]

    @property
    def downloaded_bytes(self) -> int:
        return self.fields["downloadedBytes"]

    @property
    def files_added(self) -> int:
        return self.fields["filesAdded"]

    @property
    def session_count(self) -> int:
        return self.fields["sessionCount"]

    @property
    def seconds_active(self) -> int:
        return self.fields["secondsActive"]


class SessionStats(Container):
    # https://github.com/transmission/transmission/blob/main/docs/rpc-spec.md
    # 42-session-statistics

    @property
    def active_torrent_count(self) -> int:
        return self.fields["activeTorrentCount"]

    @property
    def download_speed(self) -> int:
        return self.fields["downloadSpeed"]

    @property
    def paused_torrent_count(self) -> int:
        return self.fields["pausedTorrentCount"]

    @property
    def torrent_count(self) -> int:
        return self.fields["torrentCount"]

    @property
    def upload_speed(self) -> int:
        return self.fields["uploadSpeed"]

    @property
    def cumulative_stats(self) -> Stats:
        return Stats(fields=self.fields["cumulative-stats"])

    @property
    def current_stats(self) -> Stats:
        return Stats(fields=self.fields["current-stats"])


class Units(Container):
    # 4 strings: KB/s, MB/s, GB/s, TB/s
    @property
    def speed_units(self) -> List[str]:
        return self.fields["speed-units"]

    # number of bytes in a KB (1000 for kB; 1024 for KiB)
    @property
    def speed_bytes(self) -> int:
        return self.fields["speed-bytes"]

    # 4 strings: KB/s, MB/s, GB/s, TB/s
    @property
    def size_units(self) -> List[str]:
        return self.fields["size-units"]

    # number of bytes in a KB (1000 for kB; 1024 for KiB)
    @property
    def size_bytes(self) -> int:
        return self.fields["size-bytes"]

    # 4 strings: KB/s, MB/s, GB/s, TB/s
    @property
    def memory_units(self) -> List[str]:
        return self.fields["memory-units"]

    # number of bytes in a KB (1000 for kB; 1024 for KiB)
    @property
    def memory_bytes(self) -> int:
        return self.fields["memory-bytes"]


class Session(Container):
    """
    Session is a class holding the session data for a Transmission daemon.

    Access the session field can be done through attributes.
    The attributes available are the same as the session arguments in the
    Transmission RPC specification, but with underscore instead of hyphen.


    get ``'download-dir'`` with ``session.download_dir``.

    .. code-block:: python

        session = Client().get_session()

        current = session.download_dir

    https://github.com/transmission/transmission/blob/main/docs/rpc-spec.md#41-session-arguments

    Warnings
    --------
    setter on session's properties has been removed, please use ``Client().set_session()`` instead
    """

    @property
    def alt_speed_down(self) -> int:
        """max global download speed (KBps)"""
        return self.fields["alt-speed-down"]

    @property
    def alt_speed_enabled(self) -> bool:
        # true means use the alt speeds
        return self.fields["alt-speed-enabled"]

    @property
    def alt_speed_time_begin(self) -> int:
        """when to turn on alt speeds (units: minutes after midnight)"""
        return self.fields["alt-speed-time-begin"]

    @property
    def alt_speed_time_day(self) -> int:
        """what day(s) to turn on alt speeds (look at tr_sched_day)"""
        return self.fields["alt-speed-time-day"]

    @property
    def alt_speed_time_enabled(self) -> bool:
        """true means the scheduled on/off times are used"""
        return self.fields["alt-speed-time-enabled"]

    @property
    def alt_speed_time_end(self) -> int:
        """when to turn off alt speeds (units: same)"""
        return self.fields["alt-speed-time-end"]

    @property
    def alt_speed_up(self) -> int:
        """max global upload speed (KBps)"""
        return self.fields["alt-speed-up"]

    @property
    def blocklist_enabled(self) -> bool:
        """true means enabled"""
        return self.fields["blocklist-enabled"]

    @property
    def blocklist_size(self) -> int:
        """int of rules in the blocklist"""
        return self.fields["blocklist-size"]

    @property
    def blocklist_url(self) -> str:
        """location of the blocklist to use for `blocklist-update`"""
        return self.fields["blocklist-url"]

    @property
    def cache_size_mb(self) -> int:
        """maximum size of the disk cache (MB)"""
        return self.fields["cache-size-mb"]

    @property
    def config_dir(self) -> str:
        """location of transmission's configuration directory"""
        return self.fields["config-dir"]

    @property
    def dht_enabled(self) -> bool:
        """true means allow dht in public torrents"""
        return self.fields["dht-enabled"]

    @property
    def download_dir(self) -> str:
        """default path to download torrents"""
        return self.fields["download-dir"]

    @property
    def download_dir_free_space(self) -> int:
        """**DEPRECATED** Use the `free-space` method instead."""
        return self.fields["download-dir-free-space"]

    @property
    def download_queue_enabled(self) -> bool:
        """if true, limit how many torrents can be downloaded at once"""
        return self.fields["download-queue-enabled"]

    @property
    def download_queue_size(self) -> int:
        """max int of torrents to download at once (see download-queue-enabled)"""
        return self.fields["download-queue-size"]

    @property
    def encryption(self) -> Literal["required", "preferred", "tolerated"]:
        return self.fields["encryption"]

    @property
    def idle_seeding_limit_enabled(self) -> bool:
        """true if the seeding inactivity limit is honored by default"""
        return self.fields["idle-seeding-limit-enabled"]

    @property
    def idle_seeding_limit(self) -> int:
        """torrents we're seeding will be stopped if they're idle for this long"""
        return self.fields["idle-seeding-limit"]

    @property
    def incomplete_dir_enabled(self) -> bool:
        """true means keep torrents in incomplete-dir until done"""
        return self.fields["incomplete-dir-enabled"]

    @property
    def incomplete_dir(self) -> str:
        """path for incomplete torrents, when enabled"""
        return self.fields["incomplete-dir"]

    @property
    def lpd_enabled(self) -> bool:
        """true means allow Local Peer Discovery in public torrents"""
        return self.fields["lpd-enabled"]

    @property
    def peer_limit_global(self) -> int:
        """maximum global int of peers"""
        return self.fields["peer-limit-global"]

    @property
    def peer_limit_per_torrent(self) -> int:
        """maximum global int of peers"""
        return self.fields["peer-limit-per-torrent"]

    @property
    def peer_port_random_on_start(self) -> bool:
        """true means pick a random peer port on launch"""
        return self.fields["peer-port-random-on-start"]

    @property
    def peer_port(self) -> int:
        """port int"""
        return self.fields["peer-port"]

    @property
    def pex_enabled(self) -> bool:
        """true means allow pex in public torrents"""
        return self.fields["pex-enabled"]

    @property
    def port_forwarding_enabled(self) -> bool:
        """true means ask upstream router to forward the configured peer port to transmission using UPnP or NAT-PMP"""
        return self.fields["port-forwarding-enabled"]

    @property
    def queue_stalled_enabled(self) -> bool:
        """whether or not to consider idle torrents as stalled"""
        return self.fields["queue-stalled-enabled"]

    @property
    def queue_stalled_minutes(self) -> int:
        """torrents that are idle for N minutes aren't counted toward seed-queue-size or download-queue-size"""
        return self.fields["queue-stalled-minutes"]

    @property
    def rename_partial_files(self) -> bool:
        """true means append `.part` to incomplete files"""
        return self.fields["rename-partial-files"]

    @property
    def rpc_version_minimum(self) -> int:
        """the minimum RPC API version supported"""
        return self.fields["rpc-version-minimum"]

    @property
    def rpc_version(self) -> int:
        """the current RPC API version"""
        return self.fields["rpc-version"]

    @property
    def script_torrent_done_enabled(self) -> bool:
        """whether or not to call the `done` script"""
        return self.fields["script-torrent-done-enabled"]

    @property
    def script_torrent_done_filename(self) -> str:
        """filename of the script to run"""
        return self.fields["script-torrent-done-filename"]

    @property
    def seed_queue_enabled(self) -> bool:
        """if true, limit how many torrents can be uploaded at once"""
        return self.fields["seed-queue-enabled"]

    @property
    def seed_queue_size(self) -> int:
        """max int of torrents to uploaded at once (see seed-queue-enabled)"""
        return self.fields["seed-queue-size"]

    @property
    def seedRatioLimit(self) -> float:
        """the default seed ratio for torrents to use"""
        warnings.warn("use .seed_ratio_limit", DeprecationWarning, stacklevel=2)
        return self.fields["seedRatioLimit"]

    @property
    def seed_ratio_limit(self) -> float:
        """the default seed ratio for torrents to use"""
        return self.fields["seedRatioLimit"]

    @property
    def seedRatioLimited(self) -> bool:
        """true if seedRatioLimit is honored by default"""
        warnings.warn("use .seed_ratio_limited", DeprecationWarning, stacklevel=2)
        return self.fields["seedRatioLimited"]

    @property
    def seed_ratio_limited(self) -> bool:
        """true if seedRatioLimit is honored by default"""
        return self.fields["seedRatioLimited"]

    @property
    def speed_limit_down_enabled(self) -> bool:
        """true means enabled"""
        return self.fields["speed-limit-down-enabled"]

    @property
    def speed_limit_down(self) -> int:
        """max global download speed (KBps)"""
        return self.fields["speed-limit-down"]

    @property
    def speed_limit_up_enabled(self) -> bool:
        """true means enabled"""
        return self.fields["speed-limit-up-enabled"]

    @property
    def speed_limit_up(self) -> int:
        """max global upload speed (KBps)"""
        return self.fields["speed-limit-up"]

    @property
    def start_added_torrents(self) -> bool:
        """true means added torrents will be started right away"""
        return self.fields["start-added-torrents"]

    @property
    def trash_original_torrent_files(self) -> bool:
        """true means the .torrent file of added torrents will be deleted"""
        return self.fields["trash-original-torrent-files"]

    # see below
    @property
    def units(self) -> Units:
        return self.fields["units"]

    @property
    def utp_enabled(self) -> bool:
        """true means allow utp"""
        return self.fields["utp-enabled"]

    @property
    def version(self) -> str:
        """long version str `$version ($revision)`"""
        return self.fields["version"]

    @property
    def default_trackers(self) -> Optional[list]:
        """
        list of default trackers to use on public torrents
        new at rpc-version 17
        """
        trackers = self.get("default-trackers")
        if trackers:
            return trackers.split("\n")
        return None

    @property
    def rpc_version_semver(self) -> Optional[str]:
        """
        the current RPC API version in a semver-compatible str
        new at rpc-version 17
        """
        return self.get("rpc-version-semver")

    @property
    def script_torrent_added_enabled(self) -> Optional[bool]:
        """
        whether or not to call the `added` script
        new at rpc-version 17
        """
        return self.get("script-torrent-added-enabled")

    @property
    def script_torrent_added_filename(self) -> Optional[str]:
        """
        filename of the script to run
        new at rpc-version 17
        """
        return self.get("script-torrent-added-filename")

    @property
    def script_torrent_done_seeding_enabled(self) -> Optional[bool]:
        """
        whether or not to call the `seeding-done` script
        new at rpc-version 17
        """
        return self.get("script-torrent-done-seeding-enabled")

    @property
    def script_torrent_done_seeding_filename(self) -> Optional[str]:
        """
        filename of the script to run
        new at rpc-version 17
        """
        return self.get("script-torrent-done-seeding-filename")
