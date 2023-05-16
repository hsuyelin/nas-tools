import glob
import os
from os import environ
from os import path
from sys import path as sys_path
from time import sleep

import pytest

from qbittorrentapi import APIConnectionError
from qbittorrentapi import Client
from qbittorrentapi._version_support import (
    APP_VERSION_2_API_VERSION_MAP as api_version_map,
)
from qbittorrentapi._version_support import v
from tests.utils import CHECK_SLEEP
from tests.utils import check
from tests.utils import get_torrent
from tests.utils import mkpath
from tests.utils import retry
from tests.utils import setup_environ

QBT_VERSION, IS_QBT_DEV = setup_environ()

BASE_PATH = sys_path[0]
RESOURCES_PATH = path.join(BASE_PATH, "tests", "_resources")
assert BASE_PATH.split("/")[-1] == "qbittorrent-api"

# fmt: off
ORIG_TORRENT_URL = "https://releases.ubuntu.com/22.04.1/ubuntu-22.04.1-desktop-amd64.iso.torrent"
ORIG_TORRENT_HASH = "3b245504cf5f11bbdbe1201cea6a6bf45aee1bc0"
ORIG_TORRENT = None

TORRENT1_FILENAME = "kubuntu-22.04.2-desktop-amd64.iso.torrent"
TORRENT1_URL = "https://cdimage.ubuntu.com/kubuntu/releases/22.04/release/" + TORRENT1_FILENAME
TORRENT1_HASH = "0ee141f56407236b8acd136d56332f87674650d5"
TORRENT1_FILE_HANDLE = open(path.join(RESOURCES_PATH, TORRENT1_FILENAME), mode="rb")
TORRENT1_FILE = TORRENT1_FILE_HANDLE.read()

TORRENT2_FILENAME = "xubuntu-22.04.2-desktop-amd64.iso.torrent"
TORRENT2_URL = "https://cdimage.ubuntu.com/xubuntu/releases/22.04/release/" + TORRENT2_FILENAME
TORRENT2_HASH = "3b2dda82a16378994dbb22c49bbb91c74d2fb19c"

ROOT_FOLDER_TORRENT_FILENAME = "root_folder.torrent"
ROOT_FOLDER_TORRENT_HASH = "a14553bd936a6d496402082454a70ea7a9521adc"
ROOT_FOLDER_TORRENT_FILE_HANDLE = open(path.join(RESOURCES_PATH, ROOT_FOLDER_TORRENT_FILENAME), mode="rb")
ROOT_FOLDER_TORRENT_FILE = ROOT_FOLDER_TORRENT_FILE_HANDLE.read()
# fmt: on


@pytest.fixture(autouse=True)
def abort_if_qbittorrent_crashes(client):
    """Abort tests if qbittorrent seemingly disappears during testing."""
    try:
        client.app_version()
    except APIConnectionError:
        pytest.exit("qBittorrent crashed :(")


@pytest.fixture(autouse=True)
def skip_if_not_implemented(request, api_version):
    """Skips test if `skipif_before_api_version` marker specifies minimum API version."""
    if request.node.get_closest_marker("skipif_before_api_version"):
        version = request.node.get_closest_marker("skipif_before_api_version").args[0]
        if v(api_version) < v(version):
            pytest.skip("testing %s; needs %s or later" % (v(api_version), version))


@pytest.fixture(autouse=True)
def skip_if_implemented(request, api_version):
    """Skips test if `skipif_after_api_version` marker specifies maximum API version."""
    if request.node.get_closest_marker("skipif_after_api_version"):
        version = request.node.get_closest_marker("skipif_after_api_version").args[0]
        if v(api_version) >= v(version):
            pytest.skip("testing %s; needs before %s" % (v(api_version), version))


@pytest.fixture(scope="session", autouse=True)
def client():
    """qBittorrent Client for testing session."""
    client = Client(
        RAISE_NOTIMPLEMENTEDERROR_FOR_UNIMPLEMENTED_API_ENDPOINTS=True,
        VERBOSE_RESPONSE_LOGGING=True,
        VERIFY_WEBUI_CERTIFICATE=False,
    )
    client.auth_log_in()
    # add ORIG_TORRENT to qBittorrent
    client.torrents_add(urls=ORIG_TORRENT_URL, upload_limit=10, download_limit=10)
    check(lambda: [t.hash for t in client.torrents_info()], ORIG_TORRENT_HASH, True)
    # update preferences
    client.app.preferences = dict(
        # enable RSS fetching
        rss_processing_enabled=True,
        # prevent banning IPs
        web_ui_max_auth_fail_count=1000,
        web_ui_ban_duration=1,
    )
    return client


@pytest.fixture(scope="function")
def orig_torrent(client):
    """Torrent to remain in qBittorrent for entirety of session."""
    global ORIG_TORRENT
    if ORIG_TORRENT is None:
        ORIG_TORRENT = get_torrent(client, torrent_hash=ORIG_TORRENT_HASH)
    ORIG_TORRENT.sync_local()  # ensure torrent is up-to-date
    return ORIG_TORRENT


def new_torrent_standalone(client, torrent_hash=None, **kwargs):
    check_limit = int(10 / CHECK_SLEEP)

    def add_test_torrent(torrent_hash, **kwargs):
        for attempt in range(check_limit):
            if kwargs:
                client.torrents.add(**kwargs)
            else:
                client.torrents.add(
                    torrent_files=TORRENT1_FILE,
                    save_path=path.expanduser("~/test_download/"),
                    category="test_category",
                    is_paused=True,
                    upload_limit=1024,
                    download_limit=2048,
                    is_sequential_download=True,
                    is_first_last_piece_priority=True,
                )
                torrent_hash = TORRENT1_HASH
            try:
                return get_torrent(client, torrent_hash)
            except Exception:
                if attempt >= check_limit - 1:
                    raise
                sleep(CHECK_SLEEP)

    @retry()
    def delete_test_torrent(torrent_hash):
        client.torrents_delete(torrent_hashes=torrent_hash, delete_files=True)
        check(
            lambda: [t.hash for t in client.torrents_info()],
            torrent_hash,
            reverse=True,
            negate=True,
        )

    try:
        yield add_test_torrent(torrent_hash, **kwargs)
        delete_test_torrent(torrent_hash)
    except APIConnectionError:
        yield None  # if qBittorrent crashed, it'll get caught in abort fixture


@pytest.fixture(scope="function")
def new_torrent(client):
    """Torrent that is added on demand to qBittorrent and then removed."""
    yield next(new_torrent_standalone(client, TORRENT1_HASH))


@pytest.fixture(scope="session")
def app_version(client):
    """qBittorrent Version being used for testing."""
    if IS_QBT_DEV:
        return client.app.version
    return QBT_VERSION


@pytest.fixture(scope="session")
def api_version(client):
    """qBittorrent Web API Version being used for testing."""
    try:
        return api_version_map[QBT_VERSION]
    except KeyError as exp:
        if IS_QBT_DEV:
            return client.app.web_api_version
        raise exp


def pytest_sessionfinish(session, exitstatus):
    for fh in [TORRENT1_FILE_HANDLE, ROOT_FOLDER_TORRENT_FILE_HANDLE]:
        try:
            fh.close()
        except Exception:
            pass
    if environ.get("CI") != "true":
        client = Client()
        try:
            # remove all torrents
            for torrent in client.torrents_info():
                torrent.delete(delete_files=True)
        except Exception:
            pass
        # delete coverage files if not in CI
        for file in glob.iglob(path.join(BASE_PATH, ".coverage*")):
            os.unlink(file)
        # delete downloaded files if not in CI
        for filename in [TORRENT1_FILENAME, TORRENT2_FILENAME]:
            try:
                os.unlink(mkpath("~", filename))
            except Exception:
                pass
