import errno
import logging
import platform
from sys import version_info
from time import sleep

try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable  # noqa: F401

import pytest
import requests

from qbittorrentapi._version_support import v
from qbittorrentapi.exceptions import Conflict409Error
from qbittorrentapi.exceptions import Forbidden403Error
from qbittorrentapi.exceptions import InvalidRequest400Error
from qbittorrentapi.exceptions import TorrentFileError
from qbittorrentapi.exceptions import TorrentFileNotFoundError
from qbittorrentapi.exceptions import TorrentFilePermissionError
from qbittorrentapi.torrents import TagList
from qbittorrentapi.torrents import TorrentCategoriesDictionary
from qbittorrentapi.torrents import TorrentFilesList
from qbittorrentapi.torrents import TorrentInfoList
from qbittorrentapi.torrents import TorrentLimitsDictionary
from qbittorrentapi.torrents import TorrentPieceInfoList
from qbittorrentapi.torrents import TorrentPropertiesDictionary
from qbittorrentapi.torrents import TorrentsAddPeersDictionary
from qbittorrentapi.torrents import TrackersList
from qbittorrentapi.torrents import WebSeedsList
from tests.conftest import ROOT_FOLDER_TORRENT_FILE
from tests.conftest import ROOT_FOLDER_TORRENT_HASH
from tests.conftest import TORRENT1_FILENAME
from tests.conftest import TORRENT1_HASH
from tests.conftest import TORRENT1_URL
from tests.conftest import TORRENT2_FILENAME
from tests.conftest import TORRENT2_HASH
from tests.conftest import TORRENT2_URL
from tests.conftest import new_torrent_standalone
from tests.utils import check
from tests.utils import get_func
from tests.utils import mkpath
from tests.utils import retry


def disable_queueing(client):
    if client.app.preferences.queueing_enabled:
        client.app.set_preferences(dict(queueing_enabled=False))


def enable_queueing(client):
    if not client.app.preferences.queueing_enabled:
        client.app.set_preferences(dict(queueing_enabled=True))


# something was wrong with torrents_add on v2.0.0 (the initial version)
@pytest.mark.skipif_before_api_version("2.0.1")
@pytest.mark.parametrize(
    "client_func",
    (("torrents_add", "torrents_delete"), ("torrents.add", "torrents.delete")),
)
def test_add_delete(client, client_func):
    def download_file(url, filename=None, return_bytes=False):
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                with requests.get(url, timeout=30) as r:
                    r.raise_for_status()
                    if return_bytes:
                        return r.content
                    with open(mkpath("~/%s" % filename), "wb") as f:
                        for chunk in r.iter_content(chunk_size=1024):
                            f.write(chunk)
            except Exception if attempt < (max_attempts - 1) else ZeroDivisionError:
                pass  # throw away errors until we hit the retry limit
            else:
                return
        raise Exception("Download failed: %s" % url)

    def delete():
        get_func(client, client_func[1])(
            delete_files=True, torrent_hashes=TORRENT1_HASH
        )
        get_func(client, client_func[1])(
            delete_files=True, torrent_hashes=TORRENT2_HASH
        )
        check(
            lambda: [t.hash for t in client.torrents_info()],
            TORRENT2_HASH,
            reverse=True,
            negate=True,
        )

    def check_torrents_added(f):
        def inner(**kwargs):
            try:
                f(**kwargs)
                check(
                    lambda: [t.hash for t in client.torrents_info()],
                    TORRENT1_HASH,
                    reverse=True,
                )
                if kwargs.get("single", False) is False:
                    check(
                        lambda: [t.hash for t in client.torrents_info()],
                        TORRENT2_HASH,
                        reverse=True,
                    )
            finally:
                delete()

        return inner

    @check_torrents_added
    def add_by_filename(single):
        download_file(url=TORRENT1_URL, filename=TORRENT1_FILENAME)
        download_file(url=TORRENT2_URL, filename=TORRENT2_FILENAME)
        # send bytes as a proxy for testing python 2
        kw = {} if version_info.major == 2 else dict(encoding="utf-8")
        files = ("~/%s" % TORRENT1_FILENAME, bytes("~/%s" % TORRENT2_FILENAME, **kw))

        if single:
            assert get_func(client, client_func[0])(torrent_files=files[0]) == "Ok."
        else:
            assert get_func(client, client_func[0])(torrent_files=files) == "Ok."

    @check_torrents_added
    def add_by_filename_dict(single):
        download_file(url=TORRENT1_URL, filename=TORRENT1_FILENAME)
        download_file(url=TORRENT2_URL, filename=TORRENT2_FILENAME)

        if single:
            assert (
                get_func(client, client_func[0])(
                    torrent_files={TORRENT1_FILENAME: "~/%s" % TORRENT1_FILENAME}
                )
                == "Ok."
            )
        else:
            files = {
                TORRENT1_FILENAME: "~/%s" % TORRENT1_FILENAME,
                TORRENT2_FILENAME: "~/%s" % TORRENT2_FILENAME,
            }
            assert get_func(client, client_func[0])(torrent_files=files) == "Ok."

    @check_torrents_added
    def add_by_filehandles(single):
        download_file(url=TORRENT1_URL, filename=TORRENT1_FILENAME)
        download_file(url=TORRENT2_URL, filename=TORRENT2_FILENAME)
        files = (
            open(mkpath("~/" + TORRENT1_FILENAME), "rb"),
            open(mkpath("~/" + TORRENT2_FILENAME), "rb"),
        )

        if single:
            assert get_func(client, client_func[0])(torrent_files=files[0]) == "Ok."
        else:
            assert get_func(client, client_func[0])(torrent_files=files) == "Ok."

        for file in files:
            file.close()

    @check_torrents_added
    def add_by_bytes(single):
        files = (
            download_file(TORRENT1_URL, return_bytes=True),
            download_file(TORRENT2_URL, return_bytes=True),
        )

        if single:
            assert get_func(client, client_func[0])(torrent_files=files[0]) == "Ok."
        else:
            assert get_func(client, client_func[0])(torrent_files=files) == "Ok."

    @check_torrents_added
    def add_by_url(single):
        urls = (TORRENT1_URL, TORRENT2_URL)

        if single:
            get_func(client, client_func[0])(urls=urls[0])
        else:
            get_func(client, client_func[0])(urls=urls)

    add_by_filename(single=False)
    add_by_filename(single=True)
    add_by_filename_dict(single=False)
    add_by_filename_dict(single=True)
    add_by_url(single=False)
    add_by_url(single=True)
    add_by_filehandles(single=False)
    add_by_filehandles(single=True)
    add_by_bytes(single=False)
    add_by_bytes(single=True)


def test_add_torrent_file_fail(client, monkeypatch):
    # torrent add is wonky in python2 because of support for raw bytes...
    if version_info[0] > 2:
        with pytest.raises(TorrentFileNotFoundError):
            client.torrents_add(torrent_files="/tmp/asdfasdfasdfasdf")

        with pytest.raises(TorrentFilePermissionError):
            client.torrents_add(torrent_files="/etc/shadow")

        if platform.python_implementation() == "CPython":
            with pytest.raises(TorrentFileError):

                def fake_open(*arg, **kwargs):
                    raise IOError(errno.ENODEV)

                with monkeypatch.context() as m:
                    m.setitem(__builtins__, "open", fake_open)
                    client.torrents_add(torrent_files="/etc/hosts")


def test_close_file_fail(client, monkeypatch, caplog):
    def fake_norm_files(files):
        return {object: object}, (object,)

    def post(*args, **kwargs):
        return "OK"

    if version_info[0] > 2:
        with monkeypatch.context() as m:
            m.setattr(client, "_normalize_torrent_files", fake_norm_files)
            m.setattr(client, "_post", post)
            with caplog.at_level(logging.WARNING, logger="qbittorrentapi"):
                client.torrents_add(torrent_files=object)
                assert "Failed to close file" in caplog.text


@pytest.mark.parametrize("keep_root_folder", (True, False, None))
@pytest.mark.parametrize(
    "content_layout", (None, "Original", "Subfolder", "NoSubfolder")
)
def test_add_options(client, api_version, keep_root_folder, content_layout):
    client.torrents_delete(torrent_hashes=ROOT_FOLDER_TORRENT_HASH, delete_files=True)
    if v(api_version) >= v("2.3.0"):
        client.torrents_create_tags("option-tag")
    torrent = next(
        new_torrent_standalone(
            client=client,
            torrent_files=ROOT_FOLDER_TORRENT_FILE,
            torrent_hash=ROOT_FOLDER_TORRENT_HASH,
            save_path=mkpath("~/test_download/"),
            category="test_category",
            is_paused=True,
            upload_limit=1024,
            download_limit=2048,
            is_sequential_download=True,
            is_first_last_piece_priority=True,
            is_root_folder=keep_root_folder,
            rename="this is a new name for the torrent",
            use_auto_torrent_management=False,
            tags="option-tag",
            content_layout=content_layout,
            ratio_limit=2,
            seeding_time_limit=120,
        )
    )
    check(lambda: torrent.info.category, "test_category")
    check(
        lambda: torrent.info.state,
        ("pausedDL", "checkingResumeData"),
        reverse=True,
        any=True,
    )
    check(lambda: mkpath(torrent.info.save_path), mkpath("~/test_download/"))
    check(lambda: torrent.info.up_limit, 1024)
    check(lambda: torrent.info.dl_limit, 2048)
    check(lambda: torrent.info.seq_dl, True)
    if v(api_version) >= v("2.0.1"):
        check(lambda: torrent.info.f_l_piece_prio, True)
    if content_layout is None:
        check(
            lambda: torrent.files[0]["name"].startswith("root_folder"),
            keep_root_folder in {True, None},
        )
    check(lambda: torrent.info.name, "this is a new name for the torrent")
    check(lambda: torrent.info.auto_tmm, False)
    if v(api_version) >= v("2.6.2"):
        check(lambda: torrent.info.tags, "option-tag")

    if v(api_version) >= v("2.7"):
        # after web api v2.7...root dir is driven by content_layout
        if content_layout is None:
            should_root_dir_exists = keep_root_folder in {None, True}
        else:
            should_root_dir_exists = content_layout in {"Original", "Subfolder"}
    else:
        # before web api v2.7...it is driven by is_root_folder
        if content_layout is not None and keep_root_folder is None:
            should_root_dir_exists = content_layout in {"Original", "Subfolder"}
        else:
            should_root_dir_exists = keep_root_folder in {None, True}
    check(
        lambda: any(f["name"].startswith("root_folder") for f in torrent.files),
        should_root_dir_exists,
    )

    if v(api_version) >= v("2.8.1"):
        check(lambda: torrent.info.ratio_limit, 2)
        check(lambda: torrent.info.seeding_time_limit, 120)


@pytest.mark.skipif_before_api_version("2.8.4")
@pytest.mark.parametrize("use_download_path", (None, True, False))
def test_torrents_add_download_path(client, use_download_path):
    client.torrents_delete(torrent_hashes=ROOT_FOLDER_TORRENT_HASH, delete_files=True)
    save_path = mkpath("/tmp", "down_path_save_path_test")
    download_path = mkpath("/tmp", "down_path_test")
    torrent = next(
        new_torrent_standalone(
            client=client,
            torrent_hash=ROOT_FOLDER_TORRENT_HASH,
            torrent_files=ROOT_FOLDER_TORRENT_FILE,
            download_path=download_path,
            use_download_path=use_download_path,
            test_download_limit=1024,
            save_path=save_path,
        )
    )

    if use_download_path is False:
        check(lambda: mkpath(torrent.info.download_path), download_path, negate=True)
    else:
        check(lambda: mkpath(torrent.info.download_path), download_path)


def test_properties(client, orig_torrent):
    props = client.torrents_properties(torrent_hash=orig_torrent.hash)
    assert isinstance(props, TorrentPropertiesDictionary)


def test_trackers(client, orig_torrent):
    trackers = client.torrents_trackers(torrent_hash=orig_torrent.hash)
    assert isinstance(trackers, TrackersList)


def test_webseeds(client, orig_torrent):
    web_seeds = client.torrents_webseeds(torrent_hash=orig_torrent.hash)
    assert isinstance(web_seeds, WebSeedsList)


def test_files(client, orig_torrent):
    files = client.torrents_files(torrent_hash=orig_torrent.hash)
    assert isinstance(files, TorrentFilesList)
    assert "availability" in files[0]

    assert all(file["id"] == file["index"] for file in files)


@pytest.mark.parametrize(
    "client_func", ("torrents_piece_states", "torrents_pieceStates")
)
def test_piece_states(client, orig_torrent, client_func):
    piece_states = get_func(client, client_func)(torrent_hash=orig_torrent.hash)
    assert isinstance(piece_states, TorrentPieceInfoList)


@pytest.mark.parametrize(
    "client_func", ("torrents_piece_hashes", "torrents_pieceHashes")
)
def test_piece_hashes(client, orig_torrent, client_func):
    piece_hashes = get_func(client, client_func)(torrent_hash=orig_torrent.hash)
    assert isinstance(piece_hashes, TorrentPieceInfoList)


@pytest.mark.parametrize("trackers", ("127.0.0.1", ("127.0.0.2", "127.0.0.3")))
@pytest.mark.parametrize(
    "client_func", ("torrents_add_trackers", "torrents_addTrackers")
)
def test_add_trackers(client, trackers, client_func, new_torrent):
    get_func(client, client_func)(torrent_hash=new_torrent.hash, urls=trackers)
    check(lambda: (t.url for t in new_torrent.trackers), trackers, reverse=True)


@pytest.mark.skipif_before_api_version("2.2.0")
@pytest.mark.parametrize(
    "client_func", ("torrents_edit_tracker", "torrents_editTracker")
)
def test_edit_tracker(client, client_func, orig_torrent):
    orig_torrent.add_trackers("127.1.0.1")
    get_func(client, client_func)(
        torrent_hash=orig_torrent.hash,
        original_url="127.1.0.1",
        new_url="127.1.0.2",
    )
    check(lambda: (t.url for t in orig_torrent.trackers), "127.1.0.2", reverse=True)
    get_func(client, "torrents_remove_trackers")(
        torrent_hash=orig_torrent.hash, urls="127.1.0.2"
    )


@pytest.mark.skipif_after_api_version("2.2.0")
@pytest.mark.parametrize(
    "client_func", ("torrents_edit_tracker", "torrents_editTracker")
)
def test_edit_tracker_not_implemented(client, client_func, orig_torrent):
    with pytest.raises(NotImplementedError):
        get_func(client, client_func)()


@pytest.mark.skipif_before_api_version("2.2.0")
@pytest.mark.parametrize(
    "trackers",
    (
        ("127.2.0.1",),
        ("127.2.0.2", "127.2.0.3"),
    ),
)
@pytest.mark.parametrize(
    "client_func", ("torrents_remove_trackers", "torrents_removeTrackers")
)
def test_remove_trackers(client, trackers, client_func, orig_torrent):
    orig_torrent.add_trackers(trackers)
    get_func(client, client_func)(torrent_hash=orig_torrent.hash, urls=trackers)
    check(
        lambda: (t.url for t in orig_torrent.trackers),
        trackers,
        reverse=True,
        negate=True,
    )


@pytest.mark.skipif_after_api_version("2.2.0")
@pytest.mark.parametrize(
    "client_func", ("torrents_remove_trackers", "torrents_removeTrackers")
)
def test_remove_trackers_not_implemented(client, client_func, orig_torrent):
    with pytest.raises(NotImplementedError):
        get_func(client, client_func)()


@pytest.mark.parametrize("client_func", ("torrents_file_priority", "torrents_filePrio"))
def test_file_priority(client, orig_torrent, client_func):
    get_func(client, client_func)(
        torrent_hash=orig_torrent.hash, file_ids=0, priority=6
    )
    check(lambda: orig_torrent.files[0].priority, 6)
    get_func(client, client_func)(
        torrent_hash=orig_torrent.hash, file_ids=0, priority=7
    )
    check(lambda: orig_torrent.files[0].priority, 7)


@pytest.mark.parametrize("new_name", ("new name 2", "new_name_2"))
def test_rename(client, orig_torrent, new_name):
    client.torrents_rename(torrent_hash=orig_torrent.hash, new_torrent_name=new_name)
    check(lambda: orig_torrent.info.name.replace("+", " "), new_name)


@pytest.mark.skipif_before_api_version("2.4.0")
@pytest.mark.parametrize("new_name", ("new name file 2", "new_name_file_2"))
@pytest.mark.parametrize("client_func", ("torrents_rename_file", "torrents_renameFile"))
def test_rename_file(
    client,
    new_torrent,
    new_name,
    client_func,
):
    # pre-v4.3.3 rename_file signature
    get_func(client, client_func)(
        torrent_hash=new_torrent.hash, file_id=0, new_file_name=new_name
    )
    check(lambda: new_torrent.files[0].name.replace("+", " "), new_name)
    # test invalid file ID is rejected
    with pytest.raises(Conflict409Error):
        get_func(client, client_func)(
            torrent_hash=new_torrent.hash, file_id=10, new_file_name=new_name
        )
    # post-v4.3.3 rename_file signature
    new_new_name = new_name + "NEW"
    get_func(client, client_func)(
        torrent_hash=new_torrent.hash,
        old_path=new_torrent.files[0].name,
        new_path=new_new_name,
    )
    check(lambda: new_torrent.files[0].name.replace("+", " "), new_new_name)
    # test invalid old_path is rejected
    with pytest.raises(Conflict409Error):
        get_func(client, client_func)(
            torrent_hash=new_torrent.hash, old_path="asdf", new_path="xcvb"
        )


@pytest.mark.skipif_after_api_version("2.4.0")
@pytest.mark.parametrize("client_func", ("torrents_rename_file", "torrents_renameFile"))
def test_rename_file_not_implemented(
    client,
    new_torrent,
    client_func,
):
    with pytest.raises(NotImplementedError):
        get_func(client, client_func)()


@pytest.mark.skipif_before_api_version("2.7")
@pytest.mark.parametrize("new_name", ("asdf zxcv", "asdf_zxcv"))
@pytest.mark.parametrize(
    "client_func", ("torrents_rename_folder", "torrents_renameFolder")
)
def test_rename_folder(client, app_version, new_torrent, new_name, client_func):
    if v(app_version) >= v("v4.3.3"):
        # move the file in to a new folder
        orig_file_path = new_torrent.files[0].name
        new_folder = "qwer"
        client.torrents_rename_file(
            torrent_hash=new_torrent.hash,
            old_path=orig_file_path,
            new_path=new_folder + "/" + orig_file_path,
        )
        sleep(0.25)  # qBittorrent crashes if you make these calls too fast...
        # test rename that new folder
        get_func(client, client_func)(
            torrent_hash=new_torrent.hash,
            old_path=new_folder,
            new_path=new_name,
        )
        check(
            lambda: new_torrent.files[0].name.replace("+", " "),
            new_name + "/" + orig_file_path,
        )
    elif v(app_version) >= v("v4.3.2"):
        with pytest.raises(NotImplementedError):
            get_func(client, client_func)()


@pytest.mark.skipif_after_api_version("2.7")
@pytest.mark.parametrize(
    "client_func", ("torrents_rename_folder", "torrents_renameFolder")
)
def test_rename_folder_not_implemented(client, client_func):
    with pytest.raises(NotImplementedError):
        get_func(client, client_func)()


@pytest.mark.skipif_before_api_version("2.8.14")
def test_export(client, orig_torrent):
    assert isinstance(client.torrents_export(torrent_hash=orig_torrent.hash), bytes)


@pytest.mark.skipif_after_api_version("2.8.14")
def test_export_not_implemented(client):
    with pytest.raises(NotImplementedError):
        client.torrents_export()


@pytest.mark.parametrize("client_func", ("torrents_info", "torrents.info"))
def test_torrents_info(client, client_func):
    assert isinstance(get_func(client, client_func)(), TorrentInfoList)
    if "." in client_func:
        assert isinstance(get_func(client, client_func).all(), TorrentInfoList)
        assert isinstance(get_func(client, client_func).downloading(), TorrentInfoList)
        assert isinstance(get_func(client, client_func).seeding(), TorrentInfoList)
        assert isinstance(get_func(client, client_func).completed(), TorrentInfoList)
        assert isinstance(get_func(client, client_func).paused(), TorrentInfoList)
        assert isinstance(get_func(client, client_func).active(), TorrentInfoList)
        assert isinstance(get_func(client, client_func).inactive(), TorrentInfoList)
        assert isinstance(get_func(client, client_func).resumed(), TorrentInfoList)
        assert isinstance(get_func(client, client_func).stalled(), TorrentInfoList)
        assert isinstance(
            get_func(client, client_func).stalled_uploading(), TorrentInfoList
        )
        assert isinstance(
            get_func(client, client_func).stalled_downloading(), TorrentInfoList
        )
        assert isinstance(get_func(client, client_func).checking(), TorrentInfoList)
        assert isinstance(get_func(client, client_func).moving(), TorrentInfoList)
        assert isinstance(get_func(client, client_func).errored(), TorrentInfoList)


@pytest.mark.skipif_before_api_version("2.8.3")
@pytest.mark.parametrize("client_func", ("torrents_info", "torrents.info"))
def test_torrents_info_tag(client, new_torrent, client_func):
    tag_name = "tag_filter_name"
    client.torrents_add_tags(tags=tag_name, torrent_hashes=new_torrent.hash)
    torrents = get_func(client, client_func)(
        torrent_hashes=new_torrent.hash, tag=tag_name
    )
    assert new_torrent.hash in {t.hash for t in torrents}


# test fails on 4.1.0 release
@pytest.mark.skipif_before_api_version("2.0.1")
@pytest.mark.parametrize(
    "client_func",
    (("torrents_pause", "torrents_resume"), ("torrents.pause", "torrents.resume")),
)
def test_pause_resume(client, new_torrent, client_func):
    get_func(client, client_func[0])(torrent_hashes=new_torrent.hash)
    check(
        lambda: client.torrents_info(hashes=new_torrent.hash)[0].state_enum.is_paused,
        True,
    )

    get_func(client, client_func[1])(torrent_hashes=new_torrent.hash)
    check(
        lambda: client.torrents_info(hashes=new_torrent.hash)[0].state_enum.is_paused,
        False,
    )


def test_action_for_all_torrents(client):
    client.torrents.resume.all()
    for torrent in client.torrents.info():
        check(
            lambda: client.torrents_info(torrents_hashes=torrent.hash)[0].state,
            ("pausedDL",),
            negate=True,
        )
    client.torrents.pause.all()
    for torrent in client.torrents.info():
        check(
            lambda: client.torrents_info(torrents_hashes=torrent.hash)[0].state,
            ("stalledDL", "pausedDL"),
            any=True,
        )


@pytest.mark.parametrize("client_func", ("torrents_recheck", "torrents.recheck"))
def test_recheck(client, orig_torrent, client_func):
    get_func(client, client_func)(torrent_hashes=orig_torrent.hash)


@pytest.mark.skipif_before_api_version("2.0.2")
@pytest.mark.parametrize("client_func", ("torrents_reannounce", "torrents.reannounce"))
def test_reannounce(client, orig_torrent, client_func):
    get_func(client, client_func)(torrent_hashes=orig_torrent.hash)


@pytest.mark.skipif_after_api_version("2.0.2")
@pytest.mark.parametrize("client_func", ("torrents_reannounce", "torrents.reannounce"))
def test_reannounce_not_implemented(client, client_func):
    with pytest.raises(NotImplementedError):
        get_func(client, client_func)()


# priority doesn't seem to work on v4.1.0
@pytest.mark.skipif_before_api_version("2.0.1")
@pytest.mark.parametrize(
    "client_func",
    (
        (
            "torrents_increase_priority",
            "torrents_decrease_priority",
            "torrents_top_priority",
            "torrents_bottom_priority",
        ),
        (
            "torrents_increasePrio",
            "torrents_decreasePrio",
            "torrents_topPrio",
            "torrents_bottomPrio",
        ),
    ),
)
def test_priority(client, new_torrent, client_func):
    disable_queueing(client)

    with pytest.raises(Conflict409Error):
        get_func(client, client_func[0])(torrent_hashes=new_torrent.hash)
    with pytest.raises(Conflict409Error):
        get_func(client, client_func[1])(torrent_hashes=new_torrent.hash)
    with pytest.raises(Conflict409Error):
        get_func(client, client_func[2])(torrent_hashes=new_torrent.hash)
    with pytest.raises(Conflict409Error):
        get_func(client, client_func[3])(torrent_hashes=new_torrent.hash)

    enable_queueing(client)

    @retry()
    def test1(current_priority):
        get_func(client, client_func[0])(torrent_hashes=new_torrent.hash)
        check(lambda: new_torrent.info.priority < current_priority, True)

    @retry()
    def test2(current_priority):
        get_func(client, client_func[1])(torrent_hashes=new_torrent.hash)
        check(lambda: new_torrent.info.priority > current_priority, True)

    @retry()
    def test3(current_priority):
        get_func(client, client_func[2])(torrent_hashes=new_torrent.hash)
        check(lambda: new_torrent.info.priority < current_priority, True)

    @retry()
    def test4(current_priority):
        get_func(client, client_func[3])(torrent_hashes=new_torrent.hash)
        check(lambda: new_torrent.info.priority > current_priority, True)

    current_priority = new_torrent.info.priority
    test1(current_priority)
    current_priority = new_torrent.info.priority
    test2(current_priority)
    current_priority = new_torrent.info.priority
    test3(current_priority)
    current_priority = new_torrent.info.priority
    test4(current_priority)


@pytest.mark.parametrize(
    "client_func",
    (
        ("torrents_set_download_limit", "torrents_download_limit"),
        ("torrents_setDownloadLimit", "torrents_downloadLimit"),
        ("torrents.set_download_limit", "torrents.download_limit"),
        ("torrents.setDownloadLimit", "torrents.downloadLimit"),
    ),
)
def test_download_limit(client, client_func, orig_torrent):
    orig_download_limit = get_func(client, client_func[1])(
        torrent_hashes=orig_torrent.hash
    )[orig_torrent.hash]

    get_func(client, client_func[0])(torrent_hashes=orig_torrent.hash, limit=100)
    assert isinstance(
        get_func(client, client_func[1])(torrent_hashes=orig_torrent.hash),
        TorrentLimitsDictionary,
    )
    check(
        lambda: get_func(client, client_func[1])(torrent_hashes=orig_torrent.hash)[
            orig_torrent.hash
        ],
        100,
    )

    # reset download limit
    get_func(client, client_func[0])(
        torrent_hashes=orig_torrent.hash, limit=orig_download_limit
    )
    check(
        lambda: get_func(client, client_func[1])(torrent_hashes=orig_torrent.hash)[
            orig_torrent.hash
        ],
        orig_download_limit,
    )


@pytest.mark.parametrize(
    "client_func",
    (
        ("torrents_set_upload_limit", "torrents_upload_limit"),
        ("torrents_setUploadLimit", "torrents_uploadLimit"),
        ("torrents.set_upload_limit", "torrents.upload_limit"),
        ("torrents.setUploadLimit", "torrents.uploadLimit"),
    ),
)
def test_upload_limit(client, client_func, orig_torrent):
    orig_upload_limit = get_func(client, client_func[1])(
        torrent_hashes=orig_torrent.hash
    )[orig_torrent.hash]

    get_func(client, client_func[0])(torrent_hashes=orig_torrent.hash, limit=100)
    assert isinstance(
        get_func(client, client_func[1])(torrent_hashes=orig_torrent.hash),
        TorrentLimitsDictionary,
    )
    check(
        lambda: get_func(client, client_func[1])(torrent_hashes=orig_torrent.hash)[
            orig_torrent.hash
        ],
        100,
    )

    # reset upload limit
    get_func(client, client_func[0])(
        torrent_hashes=orig_torrent.hash, limit=orig_upload_limit
    )
    check(
        lambda: get_func(client, client_func[1])(torrent_hashes=orig_torrent.hash)[
            orig_torrent.hash
        ],
        orig_upload_limit,
    )


@pytest.mark.skipif_before_api_version("2.0.1")
@pytest.mark.parametrize(
    "client_func",
    (
        "torrents_set_share_limits",
        "torrents_setShareLimits",
        "torrents.set_share_limits",
        "torrents.setShareLimits",
    ),
)
def test_set_share_limits(client, client_func, orig_torrent):
    get_func(client, client_func)(
        ratio_limit=2, seeding_time_limit=5, torrent_hashes=orig_torrent.hash
    )
    check(lambda: orig_torrent.info.max_ratio, 2)
    check(lambda: orig_torrent.info.max_seeding_time, 5)
    get_func(client, client_func)(
        ratio_limit=3, seeding_time_limit=6, torrent_hashes=orig_torrent.hash
    )
    check(lambda: orig_torrent.info.max_ratio, 3)
    check(lambda: orig_torrent.info.max_seeding_time, 6)


@pytest.mark.skipif_after_api_version("2.0.1")
@pytest.mark.parametrize(
    "client_func",
    (
        "torrents_set_share_limits",
        "torrents_setShareLimits",
        "torrents.set_share_limits",
        "torrents.setShareLimits",
    ),
)
def test_set_share_limits_not_implemented(client, client_func):
    with pytest.raises(NotImplementedError):
        get_func(client, client_func)()


@pytest.mark.skipif_before_api_version("2.0.2")
@pytest.mark.parametrize(
    "client_func",
    (
        "torrents_set_location",
        "torrents_setLocation",
        "torrents.set_location",
        "torrents.setLocation",
    ),
)
def test_set_location(client, app_version, client_func, new_torrent):
    # stopped erroring when the write check was removed for API
    if v(app_version) < v("v4.5.2"):
        with pytest.raises(Forbidden403Error):
            get_func(client, client_func)(
                location="/etc/", torrent_hashes=new_torrent.hash
            )

    loc = mkpath("/tmp", "1")
    get_func(client, client_func)(location=loc, torrent_hashes=new_torrent.hash)
    # qBittorrent may return trailing separators depending on version....
    check(lambda: mkpath(new_torrent.info.save_path), loc, any=True)


@pytest.mark.skipif_before_api_version("2.8.4")
@pytest.mark.parametrize(
    "client_func",
    (
        "torrents_set_save_path",
        "torrents_setSavePath",
        "torrents.set_save_path",
        "torrents.setSavePath",
    ),
)
def test_set_save_path(client, client_func, new_torrent):
    with pytest.raises(Forbidden403Error):
        get_func(client, client_func)(
            save_path="/etc/", torrent_hashes=new_torrent.hash
        )
    with pytest.raises(Conflict409Error):
        get_func(client, client_func)(
            save_path="/etc/asdf", torrent_hashes=new_torrent.hash
        )

    loc = mkpath("/tmp", "savepath1")
    get_func(client, client_func)(save_path=loc, torrent_hashes=new_torrent.hash)
    # qBittorrent may return trailing separators depending on version....
    check(lambda: mkpath(new_torrent.info.save_path), loc, any=True)


@pytest.mark.skipif_after_api_version("2.8.4")
@pytest.mark.parametrize(
    "client_func",
    (
        "torrents_set_save_path",
        "torrents_setSavePath",
        "torrents.set_save_path",
        "torrents.setSavePath",
    ),
)
def test_set_save_path_not_implemented(client, client_func):
    with pytest.raises(NotImplementedError):
        get_func(client, client_func)()


@pytest.mark.skipif_before_api_version("2.8.4")
@pytest.mark.parametrize(
    "client_func",
    (
        "torrents_set_download_path",
        "torrents_setDownloadPath",
        "torrents.set_download_path",
        "torrents.setDownloadPath",
    ),
)
def test_set_download_path(client, client_func, new_torrent):
    with pytest.raises(Forbidden403Error):
        get_func(client, client_func)(
            download_path="/etc/", torrent_hashes=new_torrent.hash
        )
    with pytest.raises(Conflict409Error):
        get_func(client, client_func)(
            download_path="/etc/asdf", torrent_hashes=new_torrent.hash
        )

    loc = mkpath("/tmp", "savepath1")
    get_func(client, client_func)(download_path=loc, torrent_hashes=new_torrent.hash)
    # qBittorrent may return trailing separators depending on version....
    check(lambda: mkpath(new_torrent.info.download_path), loc, any=True)


@pytest.mark.skipif_after_api_version("2.8.4")
@pytest.mark.parametrize(
    "client_func",
    (
        "torrents_set_download_path",
        "torrents_setDownloadPath",
        "torrents.set_download_path",
        "torrents.setDownloadPath",
    ),
)
def test_set_download_path_not_implemented(client, client_func, new_torrent):
    with pytest.raises(NotImplementedError):
        get_func(client, client_func)()


@pytest.mark.parametrize(
    "client_func",
    (
        "torrents_set_category",
        "torrents_setCategory",
        "torrents.set_category",
        "torrents.setCategory",
    ),
)
@pytest.mark.parametrize("name", ("awesome cat", "awesome_cat"))
def test_set_category(client, client_func, name, orig_torrent):
    with pytest.raises(Conflict409Error):
        get_func(client, client_func)(
            category="/!@#$%^&*(", torrent_hashes=orig_torrent.hash
        )

    client.torrents_create_category(name=name)
    try:
        get_func(client, client_func)(category=name, torrent_hashes=orig_torrent.hash)
        check(lambda: orig_torrent.info.category.replace("+", " "), name)
    finally:
        client.torrents_remove_categories(categories=name)


@pytest.mark.parametrize(
    "client_func",
    (
        "torrents_set_auto_management",
        "torrents_setAutoManagement",
        "torrents.set_auto_management",
        "torrents.setAutoManagement",
    ),
)
def test_torrents_set_auto_management(client, client_func, orig_torrent):
    current_setting = orig_torrent.info.auto_tmm
    get_func(client, client_func)(
        enable=(not current_setting), torrent_hashes=orig_torrent.hash
    )
    check(lambda: orig_torrent.info.auto_tmm, (not current_setting))
    get_func(client, client_func)(
        enable=False, torrent_hashes=orig_torrent.hash
    )  # leave on False


@pytest.mark.parametrize(
    "client_func",
    (
        "torrents_toggle_sequential_download",
        "torrents_toggleSequentialDownload",
        "torrents.toggle_sequential_download",
        "torrents.toggleSequentialDownload",
    ),
)
def test_toggle_sequential_download(client, client_func, orig_torrent):
    current_setting = orig_torrent.info.seq_dl
    get_func(client, client_func)(torrent_hashes=orig_torrent.hash)
    check(lambda: orig_torrent.info.seq_dl, not current_setting)


@pytest.mark.skipif_before_api_version("2.0.1")
@pytest.mark.parametrize(
    "client_func",
    (
        "torrents_toggle_first_last_piece_priority",
        "torrents_toggleFirstLastPiecePrio",
        "torrents.toggle_first_last_piece_priority",
        "torrents.toggleFirstLastPiecePrio",
    ),
)
def test_toggle_first_last_piece_priority(client, client_func, new_torrent):
    current_setting = new_torrent.info.f_l_piece_prio
    get_func(client, client_func)(torrent_hashes=new_torrent.hash)
    check(lambda: new_torrent.info.f_l_piece_prio, not current_setting)


@pytest.mark.parametrize(
    "client_func",
    (
        "torrents_set_force_start",
        "torrents_setForceStart",
        "torrents.set_force_start",
        "torrents.setForceStart",
    ),
)
def test_set_force_start(client, client_func, orig_torrent):
    current_setting = orig_torrent.info.force_start
    get_func(client, client_func)(
        enable=(not current_setting), torrent_hashes=orig_torrent.hash
    )
    check(lambda: orig_torrent.info.force_start, not current_setting)


@pytest.mark.parametrize(
    "client_func",
    (
        "torrents_set_super_seeding",
        "torrents_setSuperSeeding",
        "torrents.set_super_seeding",
        "torrents.setSuperSeeding",
    ),
)
def test_set_super_seeding(client, client_func, orig_torrent):
    # this may or may not actually be working....
    get_func(client, client_func)(enable=False, torrent_hashes=orig_torrent.hash)
    check(lambda: orig_torrent.info.force_start, False)


@pytest.mark.skipif_before_api_version("2.3.0")
@pytest.mark.parametrize(
    "client_func",
    (
        "torrents_add_peers",
        "torrents_addPeers",
        "torrents.add_peers",
        "torrents.addPeers",
    ),
)
@pytest.mark.parametrize(
    "peers", ("127.0.0.1:5000", ("127.0.0.1:5000", "127.0.0.2:5000"), "127.0.0.1")
)
def test_torrents_add_peers(client, orig_torrent, client_func, peers):
    if all(map(lambda p: ":" not in p, peers)):
        with pytest.raises(InvalidRequest400Error):
            get_func(client, client_func)(peers=peers, torrent_hashes=orig_torrent.hash)
    else:
        p = get_func(client, client_func)(peers=peers, torrent_hashes=orig_torrent.hash)
        # can only actually verify the peer was added if it's a valid peer  # noqa: E800
        # check(  # noqa: E800
        #     lambda: client.sync_torrent_peers(torrent_hash=orig_torrent.hash)['peers'],  # noqa: E800
        #     peers,  # noqa: E800
        #     reverse=True  # noqa: E800
        # )  # noqa: E800
        assert isinstance(p, TorrentsAddPeersDictionary)


@pytest.mark.skipif_after_api_version("2.3.0")
@pytest.mark.parametrize(
    "client_func",
    (
        "torrents_add_peers",
        "torrents_addPeers",
        "torrents.add_peers",
        "torrents.addPeers",
    ),
)
def test_torrents_add_peers_not_implemented(client, client_func):
    with pytest.raises(NotImplementedError):
        get_func(client, client_func)()


def _categories_save_path_key(api_version):
    """With qBittorrent 4.4.0 (Web API 2.8.4), the key in the category
    definition returned changed from savePath to save_path...."""
    if v(api_version) == v("2.8.4"):
        return "save_path"
    return "savePath"


@pytest.mark.skipif_before_api_version("2.1.1")
def test_categories1(client):
    assert isinstance(client.torrents_categories(), TorrentCategoriesDictionary)


@pytest.mark.skipif_after_api_version("2.1.1")
def test_categories1_not_implemented(client, api_version):
    with pytest.raises(NotImplementedError):
        client.torrents_categories()


@pytest.mark.skipif_before_api_version("2.1.1")
def test_categories2(client, api_version):
    save_path_key = _categories_save_path_key(api_version)
    name = "new_category"
    client.torrent_categories.categories = {"name": name, save_path_key: "/tmp"}
    assert name in client.torrent_categories.categories
    client.torrent_categories.categories = {"name": name, save_path_key: "/tmp/new"}
    assert mkpath(client.torrent_categories.categories[name][save_path_key]) == mkpath(
        "/tmp/new"
    )
    client.torrents_remove_categories(categories=name)


@pytest.mark.skipif_after_api_version("2.1.1")
def test_categories2_not_implemented(client):
    with pytest.raises(NotImplementedError):
        _ = client.torrent_categories.categories


@pytest.mark.parametrize(
    "client_func",
    (
        "torrents_create_category",
        "torrents_createCategory",
        "torrent_categories.create_category",
        "torrent_categories.createCategory",
    ),
)
@pytest.mark.parametrize("filepath", (None, "", "/tmp/"))
@pytest.mark.parametrize("name", ("name", "name 1"))
@pytest.mark.parametrize("enable_download_path", (None, True, False))
def test_create_categories(
    client, api_version, orig_torrent, client_func, filepath, name, enable_download_path
):
    save_path = download_path = filepath
    if filepath:
        save_path += "save"
        download_path += "download"

    try:
        get_func(client, client_func)(
            name=name,
            save_path=save_path,
            download_path=download_path,
            enable_download_path=enable_download_path,
        )
        client.torrents_set_category(torrent_hashes=orig_torrent.hash, category=name)
        check(lambda: orig_torrent.info.category.replace("+", " "), name)
        if v(api_version) >= v("2.2"):
            check(
                lambda: [n.replace("+", " ") for n in client.torrents_categories()],
                name,
                reverse=True,
            )
            save_path_key = _categories_save_path_key(api_version)
            check(
                lambda: [
                    mkpath(cat[save_path_key])
                    for cat in client.torrents_categories().values()
                ],
                mkpath(save_path) or "",
                reverse=True,
            )
        if v(api_version) >= v("2.8.4") and enable_download_path is not False:
            check(
                lambda: [
                    mkpath(cat.get("download_path", ""))
                    for cat in client.torrents_categories().values()
                ],
                mkpath(download_path) or "",
                reverse=True,
            )
    finally:
        client.torrents_remove_categories(categories=name)


@pytest.mark.skipif_before_api_version("2.1.0")
@pytest.mark.parametrize(
    "client_func",
    (
        "torrents_edit_category",
        "torrents_editCategory",
        "torrent_categories.edit_category",
        "torrent_categories.editCategory",
    ),
)
@pytest.mark.parametrize("filepath", ("", "/tmp/"))
@pytest.mark.parametrize("name", ("editcategory",))
@pytest.mark.parametrize("enable_download_path", (None, True, False))
def test_edit_category(
    client, api_version, client_func, filepath, name, enable_download_path
):
    try:
        client.torrents_create_category(
            name=name, save_path="/tmp/savetmp", download_path="/tmp/savetmp"
        )
        save_path = mkpath(filepath + "save/")
        download_path = mkpath(filepath + "down/")
        get_func(client, client_func)(
            name=name,
            save_path=save_path,
            download_path=download_path,
            enable_download_path=enable_download_path,
        )
        check(
            lambda: [n.replace("+", " ") for n in client.torrents_categories()],
            name,
            reverse=True,
        )
        save_path_key = _categories_save_path_key(api_version)
        check(
            lambda: (
                mkpath(cat[save_path_key])
                for cat in client.torrents_categories().values()
            ),
            mkpath(save_path) or "",
            reverse=True,
        )
        if v(api_version) >= v("2.8.4") and enable_download_path is not False:
            check(
                lambda: [
                    mkpath(cat.get("download_path", ""))
                    for cat in client.torrents_categories().values()
                ],
                mkpath(download_path) or "",
                reverse=True,
            )
    finally:
        client.torrents_remove_categories(categories=name)


@pytest.mark.skipif_after_api_version("2.1.0")
@pytest.mark.parametrize(
    "client_func",
    (
        "torrents_edit_category",
        "torrents_editCategory",
        "torrent_categories.edit_category",
        "torrent_categories.editCategory",
    ),
)
def test_edit_category_not_implemented(client, client_func):
    with pytest.raises(NotImplementedError):
        get_func(client, client_func)()


@pytest.mark.parametrize(
    "client_func",
    (
        "torrents_remove_categories",
        "torrents_removeCategories",
        "torrent_categories.remove_categories",
        "torrent_categories.removeCategories",
    ),
)
@pytest.mark.parametrize("categories", (("category1",), ("category1", "category 2")))
def test_remove_category(client, api_version, orig_torrent, client_func, categories):
    for name in categories:
        client.torrents_create_category(name=name)
    orig_torrent.set_category(category=categories[0])
    get_func(client, client_func)(categories=categories)
    if v(api_version) >= v("2.2"):
        check(
            lambda: [n.replace("+", " ") for n in client.torrents_categories()],
            categories,
            reverse=True,
            negate=True,
        )
    check(lambda: orig_torrent.info.category, categories[0], negate=True)


@pytest.mark.skipif_before_api_version("2.3.0")
@pytest.mark.parametrize(
    "client_func",
    (
        "torrents_tags",
        "torrent_tags.tags",
    ),
)
def test_tags(client, client_func):
    try:
        assert isinstance(get_func(client, client_func)(), TagList)
    except TypeError:
        assert isinstance(get_func(client, client_func), TagList)


@pytest.mark.skipif_after_api_version("2.3.0")
@pytest.mark.parametrize(
    "client_func",
    (
        "torrents_tags",
        "torrent_tags.tags",
    ),
)
def test_tags_not_implemented(client, client_func):
    with pytest.raises(NotImplementedError):
        get_func(client, client_func)()


@pytest.mark.skipif_before_api_version("2.3.0")
def test_add_tag_though_property(client):
    name = "newtag"
    client.torrent_tags.tags = name
    assert name in client.torrent_tags.tags
    client.torrent_tags.delete_tags(name)
    assert name not in client.torrent_tags.tags


@pytest.mark.skipif_after_api_version("2.3.0")
def test_add_tag_though_property_not_implemented(client):
    with pytest.raises(NotImplementedError):
        client.torrent_tags.tags = "asdf"


@pytest.mark.skipif_before_api_version("2.3.0")
@pytest.mark.parametrize(
    "client_func",
    (
        "torrents_add_tags",
        "torrents_addTags",
        "torrent_tags.add_tags",
        "torrent_tags.addTags",
    ),
)
@pytest.mark.parametrize("tags", (("tag1",), ("tag1", "tag 2")))
def test_add_tags(client, orig_torrent, client_func, tags):
    try:
        get_func(client, client_func)(tags=tags, torrent_hashes=orig_torrent.hash)
        check(lambda: orig_torrent.info.tags, tags, reverse=True)
    finally:
        client.torrents_delete_tags(tags=tags)


@pytest.mark.skipif_after_api_version("2.3.0")
@pytest.mark.parametrize(
    "client_func",
    (
        "torrents_add_tags",
        "torrents_addTags",
        "torrent_tags.add_tags",
        "torrent_tags.addTags",
    ),
)
def test_add_tags_not_implemented(client, client_func):
    with pytest.raises(NotImplementedError):
        get_func(client, client_func)()


@pytest.mark.skipif_before_api_version("2.3.0")
@pytest.mark.parametrize(
    "client_func",
    (
        "torrents_remove_tags",
        "torrents_removeTags",
        "torrent_tags.remove_tags",
        "torrent_tags.removeTags",
    ),
)
@pytest.mark.parametrize("tags", (("tag1",), ("tag1", "tag 2")))
def test_remove_tags(client, orig_torrent, client_func, tags):
    try:
        orig_torrent.add_tags(tags=tags)
        get_func(client, client_func)(tags=tags, torrent_hashes=orig_torrent.hash)
        check(lambda: orig_torrent.info.tags, tags, reverse=True, negate=True)
    finally:
        client.torrents_delete_tags(tags=tags)


@pytest.mark.skipif_after_api_version("2.3.0")
@pytest.mark.parametrize(
    "client_func",
    (
        "torrents_remove_tags",
        "torrents_removeTags",
        "torrent_tags.remove_tags",
        "torrent_tags.removeTags",
    ),
)
def test_remove_tags_not_implemented(client, client_func):
    with pytest.raises(NotImplementedError):
        get_func(client, client_func)()


@pytest.mark.skipif_before_api_version("2.3.0")
@pytest.mark.parametrize(
    "client_func",
    (
        "torrents_create_tags",
        "torrents_createTags",
        "torrent_tags.create_tags",
        "torrent_tags.createTags",
    ),
)
@pytest.mark.parametrize("tags", (("tag1",), ("tag1", "tag 2")))
def test_create_tags(client, client_func, tags):
    try:
        get_func(client, client_func)(tags=tags)
        check(lambda: client.torrents_tags(), tags, reverse=True)
    finally:
        client.torrents_delete_tags(tags=tags)


@pytest.mark.skipif_after_api_version("2.3.0")
@pytest.mark.parametrize(
    "client_func",
    (
        "torrents_create_tags",
        "torrents_createTags",
        "torrent_tags.create_tags",
        "torrent_tags.createTags",
    ),
)
def test_create_tags_not_implemented(client, client_func):
    with pytest.raises(NotImplementedError):
        get_func(client, client_func)()


@pytest.mark.skipif_before_api_version("2.3.0")
@pytest.mark.parametrize(
    "client_func",
    (
        "torrents_delete_tags",
        "torrents_deleteTags",
        "torrent_tags.delete_tags",
        "torrent_tags.deleteTags",
    ),
)
@pytest.mark.parametrize("tags", (("tag1",), ("tag1", "tag 2")))
def test_delete_tags(client, client_func, tags):
    client.torrents_create_tags(tags=tags)
    get_func(client, client_func)(tags=tags)
    check(lambda: client.torrents_tags(), tags, reverse=True, negate=True)


@pytest.mark.skipif_after_api_version("2.3.0")
@pytest.mark.parametrize(
    "client_func",
    (
        "torrents_delete_tags",
        "torrents_deleteTags",
        "torrent_tags.delete_tags",
        "torrent_tags.deleteTags",
    ),
)
def test_delete_tags_not_implemented(client, client_func):
    with pytest.raises(NotImplementedError):
        get_func(client, client_func)()
