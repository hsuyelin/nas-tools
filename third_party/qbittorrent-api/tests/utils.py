from os import environ
from os import path
from time import sleep

import pytest
import six

from qbittorrentapi import APIConnectionError
from qbittorrentapi import Client
from qbittorrentapi._version_support import (
    APP_VERSION_2_API_VERSION_MAP as api_version_map,
)

# Amount of time to attempt a check
CHECK_TIME = 10
# Amount of time to sleep between checks
CHECK_SLEEP = 0.25


def setup_environ():
    """Set up environment for testing; ensure qBittorrent is running."""
    environ.setdefault("QBITTORRENTAPI_HOST", "localhost:8080")
    environ.setdefault("QBITTORRENTAPI_USERNAME", "admin")
    environ.setdefault("QBITTORRENTAPI_PASSWORD", "adminadmin")
    try:
        environ.setdefault("QBT_VER", Client().app.version)
    except APIConnectionError:
        raise Exception("is qBittorrent running???")

    qbt_version = environ.get("QBT_VER", "")
    qbt_version = qbt_version if qbt_version.startswith("v") else "v" + qbt_version

    environ.setdefault("IS_QBT_DEV", "" if qbt_version in api_version_map else "1")
    is_qbt_dev = environ.get("IS_QBT_DEV", "false").lower() not in ["", "false"]

    return qbt_version, is_qbt_dev


def get_func(obj, method_name):
    """Retrieve a method from an object.

    For example, ``torrents_info`` or ``torrents.info``.
    """
    for attr in method_name.split("."):
        obj = getattr(obj, attr)
    return obj


def mkpath(*user_path):
    """Create the fully qualified path to an iterable of directories and/or file."""
    if any(user_path):
        return path.abspath(path.realpath(path.expanduser(path.join(*user_path))))
    return ""


def get_torrent(client, torrent_hash):
    """Retrieve a torrent from qBittorrent."""
    try:
        # not all versions of torrents_info() support passing a hash
        return [t for t in client.torrents_info() if t.hash == torrent_hash][0]
    except Exception:
        pytest.exit("Failed to find torrent for %s" % torrent_hash)


def check(check_func, value, reverse=False, negate=False, any=False, check_time=None):
    """
    Compare the return value of an arbitrary function to expected value with
    retries. Since some requests take some time to take effect in qBittorrent,
    the retries every second for 10 seconds.

    :param check_func: callable to generate values to check
    :param value: str, int, or iterator of values to look for
    :param reverse: False: look for check_func return in value; True: look for value in check_func return
    :param negate: False: value must be found; True: value must not be found
    :param check_time: maximum number of seconds to spend checking
    :param any: False: all values must be (not) found; True: any value must be (not) found
    """

    def _do_check(_check_func_val, _v, _negate, _reverse):
        if _negate:
            if _reverse:
                # print("Looking that %s is _not_ in %s" % (_v, _check_func_val))
                assert _v not in _check_func_val
            else:
                # print("Looking that %s is _not_ in %s" % (_check_func_val, (_v,)))
                assert _check_func_val not in (_v,)
        else:
            if _reverse:
                # print("Looking for %s in %s" % (_v, _check_func_val))
                assert _v in _check_func_val
            else:
                # print("Looking for %s in %s" % (_check_func_val, (_v,)))
                assert _check_func_val in (_v,)

    if isinstance(value, (six.string_types, int)):
        value = (value,)

    check_limit = int((check_time or CHECK_TIME) / CHECK_SLEEP)
    success = False

    try:
        for i in range(check_limit):
            try:
                exp = None
                for val in value:
                    # clear any previous exceptions if any=True
                    exp = None if any else exp

                    try:
                        # get val here so pytest includes value in failures
                        check_val = check_func()
                        _do_check(check_val, val, negate, reverse)
                    except AssertionError as e:
                        exp = e

                    # fail the test on first failure if any=False
                    if not any and exp:
                        break
                    # this value passed so test succeeded if any=True
                    if any and not exp:
                        break

                # raise caught inner exception for handling
                if exp:
                    raise exp

                # test succeeded!!!!
                success = True
                break

            except AssertionError:
                if i >= check_limit:
                    raise
                sleep(CHECK_SLEEP)
    except APIConnectionError:
        raise AssertionError("qBittorrent crashed...")

    if not success:
        raise Exception("Test neither succeeded nor failed...")


def retry(retries=3):
    """Decorator to retry a function if there's an exception."""

    def inner(f):
        def wrapper(*args, **kwargs):
            for retry_count in range(retries):
                try:
                    return f(*args, **kwargs)
                except Exception:
                    if retry_count >= (retries - 1):
                        raise

        return wrapper

    return inner
