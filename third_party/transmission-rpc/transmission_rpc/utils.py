# Copyright (c) 2018-2021 Trim21 <i@trim21.me>
# Copyright (c) 2008-2014 Erik Svensson <erik.public@gmail.com>
# Licensed under the MIT license.
import base64
import pathlib
import datetime
from typing import List, Tuple, Union, BinaryIO, Optional
from urllib.parse import urlparse

from transmission_rpc import constants

UNITS = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB"]


def format_size(size: int) -> Tuple[float, str]:
    """
    Format byte size into IEC prefixes, B, KiB, MiB ...
    """
    s = float(size)
    i = 0
    while s >= 1024.0 and i < len(UNITS):
        i += 1
        s /= 1024.0
    return s, UNITS[i]


def format_speed(size: int) -> Tuple[float, str]:
    """
    Format bytes per second speed into IEC prefixes, B/s, KiB/s, MiB/s ...
    """
    (s, unit) = format_size(size)
    return s, f"{unit}/s"


def format_timedelta(delta: datetime.timedelta) -> str:
    """
    Format datetime.timedelta into <days> <hours>:<minutes>:<seconds>.
    """
    minutes, seconds = divmod(delta.seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{delta.days:d} {hours:02d}:{minutes:02d}:{seconds:02d}"


def get_torrent_arguments(rpc_version: int) -> List[str]:
    """
    Get torrent arguments for method in specified Transmission RPC version.
    """
    accessible = []
    for argument, info in constants.TORRENT_GET_ARGS.items():
        valid_version = True
        if rpc_version < info.added_version:
            valid_version = False
        if info.removed_version is not None and info.removed_version <= rpc_version:
            valid_version = False
        if valid_version:
            accessible.append(argument)
    return accessible


def _try_read_torrent(torrent: Union[BinaryIO, str, bytes, pathlib.Path]) -> Optional[str]:  # pylint: disable=R0911
    """
    if torrent should be encoded with base64, return a non-None value.
    """
    # torrent is a str, may be a url
    if isinstance(torrent, str):
        parsed_uri = urlparse(torrent)
        # torrent starts with file, read from local disk and encode it to base64 url.
        if parsed_uri.scheme in ["https", "http", "magnet"]:
            return None

        if parsed_uri.scheme in ["file"]:
            raise ValueError("support for `file://` URL has been removed.")
    elif isinstance(torrent, pathlib.Path):
        return base64.b64encode(torrent.read_bytes()).decode("utf-8")
    elif isinstance(torrent, bytes):
        return base64.b64encode(torrent).decode("utf-8")
    # maybe a file, try read content and encode it.
    elif hasattr(torrent, "read"):
        return base64.b64encode(torrent.read()).decode("utf-8")

    return None
