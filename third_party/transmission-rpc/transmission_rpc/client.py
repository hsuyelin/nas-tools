import os
import json
import time
import types
import string
import logging
import pathlib
import urllib.parse
from typing import Any, Dict, List, Type, Tuple, Union, BinaryIO, Iterable, Optional
from urllib.parse import quote

import requests
import requests.auth
import requests.exceptions
from typing_extensions import Literal, TypedDict

from transmission_rpc.error import (
    TransmissionError,
    TransmissionAuthError,
    TransmissionConnectError,
    TransmissionTimeoutError,
)
from transmission_rpc.types import Group, _Timeout
from transmission_rpc.utils import _try_read_torrent, get_torrent_arguments
from transmission_rpc.session import Session, SessionStats
from transmission_rpc.torrent import Torrent
from transmission_rpc.constants import LOGGER, DEFAULT_TIMEOUT, RpcMethod

valid_hash_char = string.digits + string.ascii_letters

_TorrentID = Union[int, str]
_TorrentIDs = Union[_TorrentID, List[_TorrentID], None]


class ResponseData(TypedDict):
    arguments: Any
    tag: int
    result: str


def ensure_location_str(s: Union[str, pathlib.Path]) -> str:
    if isinstance(s, pathlib.Path):
        if s.is_absolute():
            return str(s)

        raise ValueError(
            "using relative `pathlib.Path` as remote path is not supported in v4.",
        )

    return str(s)


def _parse_torrent_id(raw_torrent_id: Union[int, str]) -> Union[int, str]:
    if isinstance(raw_torrent_id, int):
        if raw_torrent_id >= 0:
            return raw_torrent_id
    elif isinstance(raw_torrent_id, str):
        if len(raw_torrent_id) != 40 or (set(raw_torrent_id) - set(valid_hash_char)):
            raise ValueError(f"torrent ids {raw_torrent_id} is not valid torrent id")
        return raw_torrent_id
    raise ValueError(f"{raw_torrent_id} is not valid torrent id")


def _parse_torrent_ids(args: Any) -> Union[str, List[Union[str, int]]]:
    if args is None:
        return []
    if isinstance(args, int):
        return [_parse_torrent_id(args)]
    if isinstance(args, str):
        if args == "recently-active":
            return args
        return [_parse_torrent_id(args)]
    if isinstance(args, (list, tuple)):
        return [_parse_torrent_id(item) for item in args]
    raise ValueError(f"Invalid torrent id {args}")


class Client:
    semver_version: Optional[str]  # available in transmission>=4.0.0

    def __init__(
        self,
        *,
        protocol: Literal["http", "https"] = "http",
        username: Optional[str] = None,
        password: Optional[str] = None,
        host: str = "127.0.0.1",
        port: int = 9091,
        path: str = "/transmission/rpc",
        timeout: Union[int, float] = DEFAULT_TIMEOUT,
        logger: logging.Logger = LOGGER,
    ):
        if isinstance(logger, logging.Logger):
            self.logger = logger
        else:
            raise TypeError(
                "logger must be instance of `logging.Logger`, default: logging.getLogger('transmission-rpc')"
            )
        self._query_timeout: _Timeout = timeout

        username = quote(username or "", safe="$-_.+!*'(),;&=", encoding="utf8") if username else ""
        password = ":" + quote(password or "", safe="$-_.+!*'(),;&=", encoding="utf8") if password else ""
        auth = f"{username}{password}@" if (username or password) else ""

        if path == "/transmission/":
            path = "/transmission/rpc"

        url = urllib.parse.urlunparse((protocol, f"{auth}{host}:{port}", path, None, None, None))
        self.url = str(url)
        self._sequence = 0
        self.raw_session: Dict[str, Any] = {}
        self.session_id = "0"
        self.server_version: str = "(unknown)"
        self.protocol_version: int = 17  # default 17
        self._http_session = requests.Session()
        self._http_session.trust_env = False
        self.get_session()
        self.torrent_get_arguments = get_torrent_arguments(self.rpc_version)

    @property
    def timeout(self) -> _Timeout:
        """
        Get current timeout for HTTP queries.
        """
        return self._query_timeout

    @timeout.setter
    def timeout(self, value: _Timeout) -> None:
        """
        Set timeout for HTTP queries.
        """
        if isinstance(value, (tuple, list)):
            if len(value) != 2:
                raise ValueError("timeout tuple can only include 2 numbers elements")
            for v in value:
                if not isinstance(v, (float, int)):
                    raise ValueError("element of timeout tuple can only be int of float")
            self._query_timeout = (value[0], value[1])  # for type checker
        elif value is None:
            self._query_timeout = DEFAULT_TIMEOUT
        else:
            self._query_timeout = float(value)

    @timeout.deleter
    def timeout(self) -> None:
        """
        Reset the HTTP query timeout to the default.
        """
        self._query_timeout = DEFAULT_TIMEOUT

    @property
    def _http_header(self) -> Dict[str, str]:
        return {"x-transmission-session-id": self.session_id}

    def _http_query(self, query: dict, timeout: Optional[_Timeout] = None) -> str:
        """
        Query Transmission through HTTP.
        """
        request_count = 0
        if timeout is None:
            timeout = self.timeout
        while True:
            if request_count >= 10:
                raise TransmissionError("too much request, try enable logger to see what happened")
            self.logger.debug(
                {
                    "url": self.url,
                    "headers": self._http_header,
                    "data": query,
                    "timeout": timeout,
                }
            )
            request_count += 1
            try:
                r = self._http_session.post(
                    self.url,
                    headers=self._http_header,
                    json=query,
                    timeout=timeout,
                )
            except requests.exceptions.Timeout as e:
                raise TransmissionTimeoutError("timeout when connection to transmission daemon") from e
            except requests.exceptions.ConnectionError as e:
                raise TransmissionConnectError(f"can't connect to transmission daemon: {str(e)}") from e

            self.session_id = r.headers.get("X-Transmission-Session-Id", "0")
            self.logger.debug(r.text)
            if r.status_code in {401, 403}:
                self.logger.debug(r.request.headers)
                raise TransmissionAuthError("transmission daemon require auth", original=r)
            if r.status_code != 409:
                return r.text

    def _request(
        self,
        method: RpcMethod,
        arguments: Optional[Dict[str, Any]] = None,
        ids: Optional[_TorrentIDs] = None,
        require_ids: bool = False,
        timeout: Optional[_Timeout] = None,
    ) -> dict:
        """
        Send json-rpc request to Transmission using http POST
        """
        if not isinstance(method, str):
            raise ValueError("request takes method as string")
        if arguments is None:
            arguments = {}
        if not isinstance(arguments, dict):
            raise ValueError("request takes arguments as dict")

        ids = _parse_torrent_ids(ids)
        if len(ids) > 0:
            arguments["ids"] = ids
        elif require_ids:
            raise ValueError("request require ids")

        query = {"tag": self._sequence, "method": method, "arguments": arguments}

        self._sequence += 1
        start = time.time()
        http_data = self._http_query(query, timeout)
        elapsed = time.time() - start
        self.logger.info("http request took %.3f s", elapsed)

        try:
            data: ResponseData = json.loads(http_data)
        except ValueError as error:
            self.logger.error("Error: %s", str(error))
            self.logger.error('Request: "%s"', query)
            self.logger.error('HTTP data: "%s"', http_data)
            raise TransmissionError(
                "failed to parse response as json", method=method, argument=arguments, rawResponse=http_data
            ) from error

        self.logger.debug(json.dumps(data, indent=2))
        if "result" not in data:
            raise TransmissionError(
                "Query failed, response data missing without result.",
                method=method,
                argument=arguments,
                response=data,
                rawResponse=http_data,
            )

        if data["result"] != "success":
            raise TransmissionError(
                f'Query failed with result "{data["result"]}".',
                method=method,
                argument=arguments,
                response=data,
                rawResponse=http_data,
            )

        res = data["arguments"]

        results = {}
        if method == RpcMethod.TorrentGet:
            return res
        elif method == RpcMethod.TorrentAdd:
            item = None
            if "torrent-added" in res:
                item = res["torrent-added"]
            elif "torrent-duplicate" in res:
                item = res["torrent-duplicate"]
            if item:
                results[item["id"]] = Torrent(fields=item)
            else:
                raise TransmissionError(
                    "Invalid torrent-add response.",
                    method=method,
                    argument=arguments,
                    response=data,
                    rawResponse=http_data,
                )
        elif method == RpcMethod.SessionGet:
            self.raw_session.update(res)
        elif method == RpcMethod.SessionStats:
            # older versions of T has the return data in "session-stats"
            if "session-stats" in res:
                return res["session-stats"]
            else:
                return res
        elif method in (
            RpcMethod.PortTest,
            RpcMethod.BlocklistUpdate,
            RpcMethod.FreeSpace,
            RpcMethod.TorrentRenamePath,
        ):
            return res
        else:
            return res

        return results

    def _update_server_version(self) -> None:
        """Decode the Transmission version string, if available."""
        self.semver_version = self.raw_session.get("rpc-version-semver")
        self.server_version = self.raw_session["version"]
        self.protocol_version = self.raw_session["rpc-version"]

    @property
    def rpc_version(self) -> int:
        """
        Get the Transmission RPC version. Trying to deduct if the server don't have a version value.
        """
        return self.protocol_version

    def _rpc_version_warning(self, required_version: int) -> None:
        """
        Add a warning to the log if the Transmission RPC version is lower then the provided version.
        """
        if self.rpc_version < required_version:
            self.logger.warning(
                "Using feature not supported by server. RPC version for server %d, feature introduced in %d.",
                self.rpc_version,
                required_version,
            )

    def add_torrent(
        self,
        torrent: Union[BinaryIO, str, bytes, pathlib.Path],
        timeout: Optional[_Timeout] = None,
        *,
        download_dir: Optional[str] = None,
        files_unwanted: Optional[List[int]] = None,
        files_wanted: Optional[List[int]] = None,
        paused: Optional[bool] = None,
        peer_limit: Optional[int] = None,
        priority_high: Optional[List[int]] = None,
        priority_low: Optional[List[int]] = None,
        priority_normal: Optional[List[int]] = None,
        cookies: Optional[str] = None,
        labels: Optional[Iterable[str]] = None,
        bandwidthPriority: Optional[int] = None,
    ) -> Torrent:
        """
        Add torrent to transfers list. ``torrent`` can be:

        - ``http://``, ``https://`` or  ``magnet:`` URL
        - torrent file-like object in binary mode
        - bytes of torrent content
        - ``pathlib.Path`` for local torrent file, will be read and encoded as base64.

        Warnings
        --------
        base64 string or ``file://`` protocol URL are not supported in v4.

        Parameters
        ----------
        torrent:
            torrent to add
        timeout:
            request timeout
        labels:
            Array of string labels.
            Add in rpc 17.
        bandwidthPriority:
            Priority for this transfer.
        cookies:
            One or more HTTP cookie(s).
        download_dir:
            The directory where the downloaded contents will be saved in.
        files_unwanted:
            A list of file id's that shouldn't be downloaded.
        files_wanted:
            A list of file id's that should be downloaded.
        paused:
            If True, does not start the transfer when added.
            Magnet url will always start to downloading torrents.
        peer_limit:
            Maximum number of peers allowed.
        priority_high:
            A list of file id's that should have high priority.
        priority_low:
            A list of file id's that should have low priority.
        priority_normal:
            A list of file id's that should have normal priority.
        """
        if torrent is None:
            raise ValueError("add_torrent requires data or a URI.")

        kwargs: Dict[str, Any] = {}
        if download_dir is not None:
            kwargs["download-dir"] = download_dir

        if files_unwanted is not None:
            kwargs["files-unwanted"] = files_unwanted

        if files_wanted is not None:
            kwargs["files-wanted"] = files_wanted

        if paused is not None:
            kwargs["paused"] = paused

        if peer_limit is not None:
            kwargs["peer-limit"] = peer_limit

        if priority_high is not None:
            kwargs["priority-high"] = priority_high

        if priority_low is not None:
            kwargs["priority-low"] = priority_low

        if priority_normal is not None:
            kwargs["priority-normal"] = priority_normal

        if bandwidthPriority is not None:
            kwargs["bandwidthPriority"] = bandwidthPriority

        if cookies is not None:
            kwargs["cookies"] = cookies

        if labels is not None:
            self._rpc_version_warning(17)
            kwargs["labels"] = list(labels)

        torrent_data = _try_read_torrent(torrent)
        if torrent_data:
            kwargs["metainfo"] = torrent_data
        else:
            kwargs["filename"] = torrent

        return list(self._request(RpcMethod.TorrentAdd, kwargs, timeout=timeout).values())[0]

    def remove_torrent(self, ids: _TorrentIDs, delete_data: bool = False, timeout: Optional[_Timeout] = None) -> None:
        """
        remove torrent(s) with provided id(s). Local data is removed if
        delete_data is True, otherwise not.
        """
        self._request(
            RpcMethod.TorrentRemove,
            {"delete-local-data": delete_data},
            ids,
            True,
            timeout=timeout,
        )

    def start_torrent(self, ids: _TorrentIDs, bypass_queue: bool = False, timeout: Optional[_Timeout] = None) -> None:
        """Start torrent(s) with provided id(s)"""
        method = RpcMethod.TorrentStart
        if bypass_queue:
            method = RpcMethod.TorrentStartNow
        self._request(method, {}, ids, True, timeout=timeout)

    def start_all(self, bypass_queue: bool = False, timeout: Optional[_Timeout] = None) -> None:
        """Start all torrents respecting the queue order"""
        method = RpcMethod.TorrentStart
        if bypass_queue:
            method = RpcMethod.TorrentStartNow
        torrent_list = sorted(self.get_torrents(), key=lambda t: t.queue_position)
        self._request(
            method,
            {},
            ids=[x.id for x in torrent_list],
            require_ids=True,
            timeout=timeout,
        )

    def stop_torrent(self, ids: _TorrentIDs, timeout: Optional[_Timeout] = None) -> None:
        """stop torrent(s) with provided id(s)"""
        self._request(RpcMethod.TorrentStop, {}, ids, True, timeout=timeout)

    def verify_torrent(self, ids: _TorrentIDs, timeout: Optional[_Timeout] = None) -> None:
        """verify torrent(s) with provided id(s)"""
        self._request(RpcMethod.TorrentVerify, {}, ids, True, timeout=timeout)

    def reannounce_torrent(self, ids: _TorrentIDs, timeout: Optional[_Timeout] = None) -> None:
        """Reannounce torrent(s) with provided id(s)"""
        self._request(RpcMethod.TorrentReannounce, {}, ids, True, timeout=timeout)

    def get_torrent(
        self,
        torrent_id: _TorrentID,
        arguments: Optional[Iterable[str]] = None,
        timeout: Optional[_Timeout] = None,
    ) -> Torrent:
        """
        Get information for torrent with provided id.
        ``arguments`` contains a list of field names to be returned, when None
        all fields are requested. See the Torrent class for more information.

        new argument ``format`` in rpc_version 16 is unnecessarily
        and this lib can't handle table response, So it's unsupported.

        Returns a Torrent object with the requested fields.


        Note
        ----
        It's recommended that you use torrent's info_hash as torrent id. torrent's info_hash will never change.

        Parameters
        ----------
        torrent_id:
            torrent id can be an int or a torrent info_hash (hash_string of torrent object).

        arguments:
            fetched torrent arguments, in most cases you don't need to set this,
            transmission-rpc will fetch all torrent fields it supported.

        timeout:
            requests timeout
        """
        if arguments:
            arguments = list(set(arguments) | {"id", "hashString"})
        else:
            arguments = self.torrent_get_arguments
        torrent_id = _parse_torrent_id(torrent_id)
        if torrent_id is None:
            raise ValueError("Invalid id")

        result = self._request(
            RpcMethod.TorrentGet,
            {"fields": arguments},
            torrent_id,
            require_ids=True,
            timeout=timeout,
        )

        for torrent in result["torrents"]:
            if torrent.get("hashString") == torrent_id or torrent.get("id") == torrent_id:
                return Torrent(fields=torrent)
        raise KeyError("Torrent not found in result")

    def get_torrents(
        self,
        ids: Optional[_TorrentIDs] = None,
        arguments: Optional[Iterable[str]] = None,
        timeout: Optional[_Timeout] = None,
    ) -> List[Torrent]:
        """
        Get information for torrents with provided ids. For more information see ``get_torrent``.

        Returns a list of Torrent object.
        """
        if arguments:
            arguments = list(set(arguments) | {"id", "hashString"})
        else:
            arguments = self.torrent_get_arguments
        return [
            Torrent(fields=x)
            for x in self._request(RpcMethod.TorrentGet, {"fields": arguments}, ids, timeout=timeout)["torrents"]
        ]

    def get_recently_active_torrents(
        self, arguments: Optional[Iterable[str]] = None, timeout: Optional[_Timeout] = None
    ) -> Tuple[List[Torrent], List[int]]:
        """
        Get information for torrents for recently active torrent. If you want to get recently-removed
        torrents. you should use this method.

        Returns
        -------
        active_torrents: List[Torrent]
            List of recently active torrents
        removed_torrents: List[int]
            List of torrent-id of recently-removed torrents.
        """
        if arguments:
            arguments = list(set(arguments) | {"id", "hashString"})
        else:
            arguments = self.torrent_get_arguments

        result = self._request(RpcMethod.TorrentGet, {"fields": arguments}, "recently-active", timeout=timeout)

        return [Torrent(fields=x) for x in result["torrents"]], result["removed"]

    def change_torrent(
        self,
        ids: _TorrentIDs,
        timeout: Optional[_Timeout] = None,
        *,
        bandwidth_priority: Optional[int] = None,
        download_limit: Optional[int] = None,
        download_limited: Optional[bool] = None,
        upload_limit: Optional[int] = None,
        upload_limited: Optional[bool] = None,
        files_unwanted: Optional[Iterable[int]] = None,
        files_wanted: Optional[Iterable[int]] = None,
        honors_session_limits: Optional[bool] = None,
        location: Optional[str] = None,
        peer_limit: Optional[int] = None,
        priority_high: Optional[Iterable[int]] = None,
        priority_low: Optional[Iterable[int]] = None,
        priority_normal: Optional[Iterable[int]] = None,
        queue_position: Optional[int] = None,
        seed_idle_limit: Optional[int] = None,
        seed_idle_mode: Optional[int] = None,
        seed_ratio_limit: Optional[float] = None,
        seed_ratio_mode: Optional[int] = None,
        tracker_add: Optional[Iterable[str]] = None,
        tracker_remove: Optional[Iterable[int]] = None,
        tracker_replace: Optional[Iterable[Tuple[int, str]]] = None,
        labels: Optional[Iterable[str]] = None,
        group: Optional[str] = None,
        tracker_list: Optional[Iterable[Iterable[str]]] = None,
        **kwargs: Any,
    ) -> None:
        """Change torrent parameters for the torrent(s) with the supplied id's.

        Parameters
        ----------
        ids
            torrent(s) to change.
        timeout
            requesst timeout.
        honors_session_limits
            true if session upload limits are honored.
        location
            new location of the torrent's content
        peer_limit
            maximum number of peers
        queue_position
            position of this torrent in its queue [0...n)
        files_wanted
            Array of file id to download.
        files_unwanted
            Array of file id to not download.
        download_limit
            maximum download speed (KBps)
        download_limited
            true if ``download_limit`` is honored
        upload_limit
            maximum upload speed (KBps)
        upload_limited
            true if ``upload_limit`` is honored
        bandwidth_priority
            Priority for this transfer.
        priority_high
            list of file id to set high download priority
        priority_low
            list of file id to set low download priority
        priority_normal
            list of file id to set normal download priority
        seed_ratio_limit
            Seed inactivity limit in minutes.
        seed_ratio_mode
            Which ratio to use.

            0 = Use session limit

            1 = Use transfer limit

            2 = Disable limit.
        seed_idle_limit
            torrent-level seeding ratio
        seed_idle_mode
            Seed inactivity mode.

            0 = Use session limit

            1 = Use transfer limit

            2 = Disable limit.
        tracker_add
            Array of string with announce URLs to add.
        tracker_remove
            Array of ids of trackers to remove.
        tracker_replace
            Array of (id, url) tuples where the announce URL should be replaced.
        labels
            Array of string labels.
            Add in rpc 16.
        group
            The name of this torrent's bandwidth group.
            Add in rpc 17.
        tracker_list
            A ``Iterable[Iterable[str]]``, each ``Iterable[str]`` for a tracker tier.
            Add in rpc 17.


        Warnings
        ----
        ``kwargs`` is for the future features not supported yet, it's not compatibility promising.

        it will be bypassed to request arguments.
        """

        args: Dict[str, Any] = {}

        if bandwidth_priority is not None:
            args["bandwidthPriority"] = bandwidth_priority

        if download_limit is not None:
            args["downloadLimit"] = download_limit
        if download_limited is not None:
            args["downloadLimited"] = download_limited
        if upload_limit is not None:
            args["uploadLimit"] = upload_limit
        if upload_limited is not None:
            args["uploadLimited"] = upload_limited
        if files_unwanted is not None:
            args["files-unwanted"] = list(files_unwanted)
        if files_wanted is not None:
            args["files-wanted"] = list(files_wanted)
        if honors_session_limits is not None:
            args["honorsSessionLimits"] = honors_session_limits
        if location is not None:
            args["location"] = location
        if peer_limit is not None:
            args["peer-limit"] = peer_limit
        if priority_high is not None:
            args["priority-high"] = list(priority_high)
        if priority_low is not None:
            args["priority-low"] = list(priority_low)
        if priority_normal is not None:
            args["priority-normal"] = list(priority_normal)
        if queue_position is not None:
            args["queuePosition"] = queue_position
        if seed_idle_limit is not None:
            args["seedIdleLimit"] = seed_idle_limit
        if seed_idle_mode is not None:
            args["seedIdleMode"] = seed_idle_mode
        if seed_ratio_limit is not None:
            args["seedRatioLimit"] = seed_ratio_limit
        if seed_ratio_mode is not None:
            args["seedRatioMode"] = seed_ratio_mode
        if tracker_add is not None:
            args["trackerAdd"] = tracker_add
        if tracker_remove is not None:
            args["trackerRemove"] = tracker_remove
        if tracker_replace is not None:
            args["trackerReplace"] = tracker_replace
        if labels is not None:
            self._rpc_version_warning(16)
            args["labels"] = list(labels)

        if tracker_list is not None:
            self._rpc_version_warning(17)
            args["trackerList"] = " ".join("\n".join(x) for x in tracker_list)

        if group is not None:
            self._rpc_version_warning(17)
            args["group"] = str(group)

        args.update(kwargs)

        if args:
            self._request(RpcMethod.TorrentSet, args, ids, True, timeout=timeout)
        else:
            ValueError("No arguments to set")

    def move_torrent_data(
        self,
        ids: _TorrentIDs,
        location: Union[str, pathlib.Path],
        timeout: Optional[_Timeout] = None,
    ) -> None:
        """Move torrent data to the new location."""
        args = {"location": ensure_location_str(location), "move": True}
        self._request(RpcMethod.TorrentSetLocation, args, ids, True, timeout=timeout)

    def locate_torrent_data(
        self,
        ids: _TorrentIDs,
        location: Union[str, pathlib.Path],
        timeout: Optional[_Timeout] = None,
    ) -> None:
        """Locate torrent data at the provided location."""
        args = {"location": ensure_location_str(location), "move": False}
        self._request(RpcMethod.TorrentSetLocation, args, ids, True, timeout=timeout)

    def rename_torrent_path(
        self,
        torrent_id: _TorrentID,
        location: Union[str, pathlib.Path],
        name: str,
        timeout: Optional[_Timeout] = None,
    ) -> Tuple[str, str]:
        """
        https://github.com/transmission/transmission/blob/main/docs/rpc-spec.md#37-renaming-a-torrents-path

        This method can only be called on single torrent.
        """
        self._rpc_version_warning(15)
        torrent_id = _parse_torrent_id(torrent_id)
        name = name.strip()  # https://github.com/trim21/transmission-rpc/issues/185
        dirname = os.path.dirname(name)
        if len(dirname) > 0:
            raise ValueError("Target name cannot contain a path delimiter")
        result = self._request(
            RpcMethod.TorrentRenamePath,
            {"path": ensure_location_str(location), "name": name},
            torrent_id,
            True,
            timeout=timeout,
        )
        return result["path"], result["name"]

    def queue_top(self, ids: _TorrentIDs, timeout: Optional[_Timeout] = None) -> None:
        """Move transfer to the top of the queue:_Timeout."""
        self._request(RpcMethod.QueueMoveTop, ids=ids, require_ids=True, timeout=timeout)

    def queue_bottom(self, ids: _TorrentIDs, timeout: Optional[_Timeout] = None) -> None:
        """Move transfer to the bottom of the queue."""
        self._request(RpcMethod.QueueMoveBottom, ids=ids, require_ids=True, timeout=timeout)

    def queue_up(self, ids: _TorrentIDs, timeout: Optional[_Timeout] = None) -> None:
        """Move transfer up in the queue."""
        self._request(RpcMethod.QueueMoveUp, ids=ids, require_ids=True, timeout=timeout)

    def queue_down(self, ids: _TorrentIDs, timeout: Optional[_Timeout] = None) -> None:
        """Move transfer down in the queue."""
        self._request(RpcMethod.QueueMoveDown, ids=ids, require_ids=True, timeout=timeout)

    def get_session(self, timeout: Optional[_Timeout] = None) -> Session:
        """
        Get session parameters. See the Session class for more information.
        """
        self._request(RpcMethod.SessionGet, timeout=timeout)
        self._update_server_version()
        return Session(fields=self.raw_session)

    def set_session(
        self,
        timeout: Optional[_Timeout] = None,
        *,
        alt_speed_down: Optional[int] = None,
        alt_speed_enabled: Optional[bool] = None,
        alt_speed_time_begin: Optional[int] = None,
        alt_speed_time_day: Optional[int] = None,
        alt_speed_time_enabled: Optional[bool] = None,
        alt_speed_time_end: Optional[int] = None,
        alt_speed_up: Optional[int] = None,
        blocklist_enabled: Optional[bool] = None,
        blocklist_url: Optional[str] = None,
        cache_size_mb: Optional[int] = None,
        dht_enabled: Optional[bool] = None,
        default_trackers: Optional[Iterable[str]] = None,
        download_dir: Optional[str] = None,
        download_queue_enabled: Optional[bool] = None,
        download_queue_size: Optional[int] = None,
        encryption: Optional[Literal["required", "preferred", "tolerated"]] = None,
        idle_seeding_limit: Optional[int] = None,
        idle_seeding_limit_enabled: Optional[bool] = None,
        incomplete_dir: Optional[str] = None,
        incomplete_dir_enabled: Optional[bool] = None,
        lpd_enabled: Optional[bool] = None,
        peer_limit_global: Optional[int] = None,
        peer_limit_per_torrent: Optional[int] = None,
        peer_port: Optional[int] = None,
        peer_port_random_on_start: Optional[bool] = None,
        pex_enabled: Optional[bool] = None,
        port_forwarding_enabled: Optional[bool] = None,
        queue_stalled_enabled: Optional[bool] = None,
        queue_stalled_minutes: Optional[int] = None,
        rename_partial_files: Optional[bool] = None,
        script_torrent_done_enabled: Optional[bool] = None,
        script_torrent_done_filename: Optional[str] = None,
        seed_queue_enabled: Optional[bool] = None,
        seed_queue_size: Optional[int] = None,
        seed_ratio_limit: Optional[int] = None,
        seed_ratio_limited: Optional[bool] = None,
        speed_limit_down: Optional[int] = None,
        speed_limit_down_enabled: Optional[bool] = None,
        speed_limit_up: Optional[int] = None,
        speed_limit_up_enabled: Optional[bool] = None,
        start_added_torrents: Optional[bool] = None,
        trash_original_torrent_files: Optional[bool] = None,
        utp_enabled: Optional[bool] = None,
        script_torrent_done_seeding_filename: Optional[str] = None,
        script_torrent_done_seeding_enabled: Optional[bool] = None,
        script_torrent_added_enabled: Optional[bool] = None,
        script_torrent_added_filename: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Set session parameters.

        Parameters
        ----------
        timeout
            request timeout
        alt_speed_down:
            max global download speed (KBps)
        alt_speed_enabled:
            true means use the alt speeds
        alt_speed_time_begin:
            Time when alternate speeds should be enabled. Minutes after midnight.
        alt_speed_time_day:
            Enables alternate speeds scheduling these days.
        alt_speed_time_enabled:
            Enables alternate speeds scheduling.
        alt_speed_time_end:
            Time when alternate speeds should be disabled. Minutes after midnight.
        alt_speed_up:
            Alternate session upload speed limit (in Kib/s).
        blocklist_enabled:
            Enables the block list
        blocklist_url:
            Location of the block list. Updated with blocklist-update.
        cache_size_mb:
            The maximum size of the disk cache in MB
        default_trackers:
            List of default trackers to use on public torrents.
        dht_enabled:
            Enables DHT.
        download_dir:
            Set the session download directory.
        download_queue_enabled:
            Enables download queue.
        download_queue_size:
            Number of slots in the download queue.
        encryption:
            Set the session encryption mode, one of ``required``, ``preferred`` or ``tolerated``.
        idle_seeding_limit:
            The default seed inactivity limit in minutes.
        idle_seeding_limit_enabled:
            Enables the default seed inactivity limit
        incomplete_dir:
            The path to the directory of incomplete transfer data.
        incomplete_dir_enabled:
            Enables the incomplete transfer data directory,
            Otherwise data for incomplete transfers are stored in the download target.
        lpd_enabled:
            Enables local peer discovery for public torrents.
        peer_limit_global:
            Maximum number of peers.
        peer_limit_per_torrent:
            Maximum number of peers per transfer.
        peer_port:
            Peer port.
        peer_port_random_on_start:
            Enables randomized peer port on start of Transmission.
        pex_enabled:
            Allowing PEX in public torrents.
        port_forwarding_enabled:
            Enables port forwarding.
        queue_stalled_enabled:
            Enable tracking of stalled transfers.
        queue_stalled_minutes:
            Number of minutes of idle that marks a transfer as stalled.
        rename_partial_files:
            Appends ".part" to incomplete files

        seed_queue_enabled:
            Enables upload queue.
        seed_queue_size:
            Number of slots in the upload queue.
        seed_ratio_limit:
            Seed ratio limit. 1.0 means 1:1 download and upload ratio.
        seed_ratio_limited:
            Enables seed ration limit.
        speed_limit_down:
            Download speed limit (in Kib/s).
        speed_limit_down_enabled:
            Enables download speed limiting.
        speed_limit_up:
            Upload speed limit (in Kib/s).
        speed_limit_up_enabled:
            Enables upload speed limiting.
        start_added_torrents:
            Added torrents will be started right away.
        trash_original_torrent_files:
            The .torrent file of added torrents will be deleted.
        utp_enabled:
            Enables Micro Transport Protocol (UTP).
        script_torrent_done_enabled:
            Whether to call the "done" script.
        script_torrent_done_filename:
            Filename of the script to run when the transfer is done.
        script_torrent_added_filename:
            filename of the script to run
        script_torrent_added_enabled:
            whether or not to call the ``added`` script
        script_torrent_done_seeding_enabled:
            whether or not to call the ``seeding-done`` script
        script_torrent_done_seeding_filename:
            filename of the script to run

        Warnings
        ----
        ``kwargs`` is for the future features not supported yet, it's not compatibility promising.

        it will be bypassed to request arguments.
        """
        args: Dict[str, Any] = {}

        if alt_speed_down is not None:
            args["alt-speed-down"] = alt_speed_down
        if alt_speed_enabled is not None:
            args["alt-speed-enabled"] = alt_speed_enabled
        if alt_speed_time_begin is not None:
            args["alt-speed-time-begin"] = alt_speed_time_begin
        if alt_speed_time_day is not None:
            args["alt-speed-time-day"] = alt_speed_time_day
        if alt_speed_time_enabled is not None:
            args["alt-speed-time-enabled"] = alt_speed_time_enabled
        if alt_speed_time_end is not None:
            args["alt-speed-time-end"] = alt_speed_time_end
        if alt_speed_up is not None:
            args["alt-speed-up"] = alt_speed_up
        if blocklist_enabled is not None:
            args["blocklist-enabled"] = blocklist_enabled
        if blocklist_url is not None:
            args["blocklist-url"] = blocklist_url
        if cache_size_mb is not None:
            args["cache-size-mb"] = cache_size_mb
        if dht_enabled is not None:
            args["dht-enabled"] = dht_enabled
        if download_dir is not None:
            args["download-dir"] = download_dir
        if download_queue_enabled is not None:
            args["download-queue-enabled"] = download_queue_enabled
        if download_queue_size is not None:
            args["download-queue-size"] = download_queue_size
        if encryption is not None:
            if encryption not in ["required", "preferred", "tolerated"]:
                raise ValueError("Invalid encryption value")
            args["encryption"] = encryption
        if idle_seeding_limit_enabled is not None:
            args["idle-seeding-limit-enabled"] = idle_seeding_limit_enabled
        if idle_seeding_limit is not None:
            args["idle-seeding-limit"] = idle_seeding_limit
        if incomplete_dir is not None:
            args["incomplete-dir"] = incomplete_dir
        if incomplete_dir_enabled is not None:
            args["incomplete-dir-enabled"] = incomplete_dir_enabled
        if lpd_enabled is not None:
            args["lpd-enabled"] = lpd_enabled
        if peer_limit_global is not None:
            args["peer-limit-global"] = peer_limit_global
        if peer_limit_per_torrent is not None:
            args["peer-limit-per-torrent"] = peer_limit_per_torrent
        if peer_port_random_on_start is not None:
            args["peer-port-random-on-start"] = peer_port_random_on_start
        if peer_port is not None:
            args["peer-port"] = peer_port
        if pex_enabled is not None:
            args["pex-enabled"] = pex_enabled
        if port_forwarding_enabled is not None:
            args["port-forwarding-enabled"] = port_forwarding_enabled
        if queue_stalled_enabled is not None:
            args["queue-stalled-enabled"] = queue_stalled_enabled
        if queue_stalled_minutes is not None:
            args["queue-stalled-minutes"] = queue_stalled_minutes
        if rename_partial_files is not None:
            args["rename-partial-files"] = rename_partial_files
        if script_torrent_done_enabled is not None:
            args["script-torrent-done-enabled"] = script_torrent_done_enabled
        if script_torrent_done_filename is not None:
            args["script-torrent-done-filename"] = script_torrent_done_filename
        if seed_queue_enabled is not None:
            args["seed-queue-enabled"] = seed_queue_enabled
        if seed_queue_size is not None:
            args["seed-queue-size"] = seed_queue_size
        if seed_ratio_limit is not None:
            args["seedRatioLimit"] = seed_ratio_limit
        if seed_ratio_limited is not None:
            args["seedRatioLimited"] = seed_ratio_limited
        if speed_limit_down is not None:
            args["speed-limit-down"] = speed_limit_down
        if speed_limit_down_enabled is not None:
            args["speed-limit-down-enabled"] = speed_limit_down_enabled
        if speed_limit_up is not None:
            args["speed-limit-up"] = speed_limit_up
        if speed_limit_up_enabled is not None:
            args["speed-limit-up-enabled"] = speed_limit_up_enabled
        if start_added_torrents is not None:
            args["start-added-torrents"] = start_added_torrents
        if trash_original_torrent_files is not None:
            args["trash-original-torrent-files"] = trash_original_torrent_files
        if utp_enabled is not None:
            args["utp-enabled"] = utp_enabled

        if default_trackers is not None:
            self._rpc_version_warning(17)
            args["default-trackers"] = "\n".join(default_trackers)

        if script_torrent_done_seeding_filename is not None:
            self._rpc_version_warning(17)
            args["script-torrent-done-seeding-filename"] = script_torrent_done_seeding_filename
        if script_torrent_done_seeding_enabled is not None:
            self._rpc_version_warning(17)
            args["script-torrent-done-seeding-enabled"] = script_torrent_done_seeding_enabled
        if script_torrent_added_enabled is not None:
            self._rpc_version_warning(17)
            args["script-torrent-added-enabled"] = script_torrent_added_enabled
        if script_torrent_added_filename is not None:
            self._rpc_version_warning(17)
            args["script-torrent-added-filename"] = script_torrent_added_filename

        args.update(kwargs)

        if args:
            self._request(RpcMethod.SessionSet, args, timeout=timeout)

    def blocklist_update(self, timeout: Optional[_Timeout] = None) -> Optional[int]:
        """Update block list. Returns the size of the block list."""
        result = self._request(RpcMethod.BlocklistUpdate, timeout=timeout)
        return result.get("blocklist-size")

    def port_test(self, timeout: Optional[_Timeout] = None) -> Optional[bool]:
        """
        Tests to see if your incoming peer port is accessible from the
        outside world.
        """
        result = self._request(RpcMethod.PortTest, timeout=timeout)
        return result.get("port-is-open")

    def free_space(self, path: Union[str, pathlib.Path], timeout: Optional[_Timeout] = None) -> Optional[int]:
        """
        Get the amount of free space (in bytes) at the provided location.
        """
        self._rpc_version_warning(15)
        path = ensure_location_str(path)
        result: Dict[str, Any] = self._request(RpcMethod.FreeSpace, {"path": path}, timeout=timeout)
        if result["path"] == path:
            return result["size-bytes"]
        return None

    def session_stats(self, timeout: Optional[_Timeout] = None) -> SessionStats:
        """Get session statistics"""
        result = self._request(RpcMethod.SessionStats, timeout=timeout)
        return SessionStats(fields=result)

    def set_group(
        self,
        name: str,
        *,
        timeout: Optional[_Timeout] = None,
        honors_session_limits: Optional[bool] = None,
        speed_limit_down: Optional[int] = None,
        speed_limit_up_enabled: Optional[bool] = None,
        speed_limit_up: Optional[int] = None,
        speed_limit_down_enabled: Optional[bool] = None,
    ) -> None:
        self._rpc_version_warning(17)
        arguments: Dict[str, Any] = {"name": name}

        if honors_session_limits is not None:
            arguments["honorsSessionLimits"] = honors_session_limits

        if speed_limit_down is not None:
            arguments["speed-limit-down"] = speed_limit_down

        if speed_limit_up_enabled is not None:
            arguments["speed-limit-up-enabled"] = speed_limit_up_enabled

        if speed_limit_up is not None:
            arguments["speed-limit-up"] = speed_limit_up

        if speed_limit_down_enabled is not None:
            arguments["speed-limit-down-enabled"] = speed_limit_down_enabled

        self._request(RpcMethod.GroupSet, arguments, timeout=timeout)

    def get_group(self, name: str, *, timeout: Optional[_Timeout] = None) -> Optional[Group]:
        self._rpc_version_warning(17)
        result: Dict[str, Any] = self._request(RpcMethod.GroupGet, {"group": name}, timeout=timeout)

        if result["arguments"]["group"]:
            return Group(fields=result["arguments"]["group"][0])
        return None

    def get_groups(self, name: Optional[List[str]] = None, *, timeout: Optional[_Timeout] = None) -> Dict[str, Group]:
        payload = {}
        if name is not None:
            payload = {"group": name}

        result: Dict[str, Any] = self._request(RpcMethod.GroupGet, payload, timeout=timeout)

        return {x["name"]: Group(fields=x) for x in result["arguments"]["group"]}

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, exc_type: Type[Exception], exc_val: Exception, exc_tb: types.TracebackType) -> None:
        self._http_session.close()
