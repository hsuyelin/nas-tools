import platform
from time import sleep

import pytest

from qbittorrentapi import Conflict409Error
from qbittorrentapi import TorrentDictionary
from qbittorrentapi import TorrentFilesList
from qbittorrentapi import TorrentPieceInfoList
from qbittorrentapi import TorrentPropertiesDictionary
from qbittorrentapi import TorrentStates
from qbittorrentapi import TrackersList
from qbittorrentapi import WebSeedsList
from qbittorrentapi._version_support import v
from tests.conftest import get_func
from tests.test_torrents import check
from tests.test_torrents import disable_queueing
from tests.test_torrents import enable_queueing
from tests.test_torrents import mkpath
from tests.test_torrents import torrent1_hash
from tests.test_torrents import torrent1_url


def test_info(orig_torrent, monkeypatch):
    assert orig_torrent.info.hash == orig_torrent.hash
    # mimic <=v2.0.1 where torrents_info() doesn't support hash arg
    orig_torrent._client._MOCK_WEB_API_VERSION = "2"
    assert orig_torrent.info.hash == orig_torrent.hash
    orig_torrent._client._MOCK_WEB_API_VERSION = None

    # ensure if things are really broken, an empty TorrentDictionary is returned...
    if platform.python_implementation() == "CPython":
        with monkeypatch.context() as m:

            def fake_info(*args, **kwargs):
                return []

            m.setattr(orig_torrent._client, "torrents_info", fake_info)
            assert isinstance(orig_torrent.info, TorrentDictionary)
            assert bool(orig_torrent.info) is False


def test_sync_local(orig_torrent):
    orig_torrent.state = "gibberish"
    assert orig_torrent.state == "gibberish"
    orig_torrent.sync_local()
    assert isinstance(orig_torrent, TorrentDictionary)
    assert orig_torrent.state != "gibberish"


def test_state_enum(orig_torrent):
    assert orig_torrent.state_enum in TorrentStates
    assert orig_torrent.state_enum is not TorrentStates.UNKNOWN
    check(lambda: orig_torrent.state_enum.is_downloading, True)
    # simulate an unknown torrent.state
    orig_torrent.state = "gibberish"
    assert orig_torrent.state_enum is TorrentStates.UNKNOWN
    # restore torrent state
    orig_torrent.sync_local()
    check(lambda: orig_torrent.state_enum.is_downloading, True)


def test_pause_resume(client, orig_torrent):
    orig_torrent.pause()
    check(
        lambda: client.torrents_info(torrents_hashes=orig_torrent.hash)[0].state,
        ("stalledDL", "pausedDL"),
        any=True,
    )

    orig_torrent.resume()
    check(
        lambda: client.torrents_info(torrents_hashes=orig_torrent.hash)[0].state,
        ("pausedDL",),
        negate=True,
        check_limit=20,
    )


def test_delete(client):
    client.torrents_add(urls=torrent1_url)
    check(lambda: [t.hash for t in client.torrents_info()], torrent1_hash, reverse=True)
    torrent = [t for t in client.torrents_info() if t.hash == torrent1_hash][0]
    sleep(1)
    torrent.delete(delete_files=True)
    check(
        lambda: [t.hash for t in client.torrents_info()],
        torrent1_hash,
        reverse=True,
        negate=True,
    )


@pytest.mark.parametrize(
    "client_func",
    (
        ("increase_priority", "decrease_priority", "top_priority", "bottom_priority"),
        ("increasePrio", "decreasePrio", "topPrio", "bottomPrio"),
    ),
)
def test_priority(client, new_torrent, client_func):
    disable_queueing(client)

    with pytest.raises(Conflict409Error):
        get_func(new_torrent, client_func[0])()
    with pytest.raises(Conflict409Error):
        get_func(new_torrent, client_func[1])()
    with pytest.raises(Conflict409Error):
        get_func(new_torrent, client_func[2])()
    with pytest.raises(Conflict409Error):
        get_func(new_torrent, client_func[3])()

    enable_queueing(client)
    sleep(1)  # putting sleeps in since these keep crashing qbittorrent

    current_priority = new_torrent.info.priority
    get_func(new_torrent, client_func[0])()
    sleep(1)
    check(lambda: new_torrent.info.priority < current_priority, True)

    current_priority = new_torrent.info.priority
    get_func(new_torrent, client_func[1])()
    sleep(1)
    check(lambda: new_torrent.info.priority > current_priority, True)

    current_priority = new_torrent.info.priority
    get_func(new_torrent, client_func[2])()
    sleep(1)
    check(lambda: new_torrent.info.priority < current_priority, True)

    current_priority = new_torrent.info.priority
    get_func(new_torrent, client_func[3])()
    sleep(1)
    check(lambda: new_torrent.info.priority > current_priority, True)


@pytest.mark.parametrize("client_func", ("set_share_limits", "setShareLimits"))
def test_set_share_limits(api_version, orig_torrent, client_func):
    if v(api_version) >= v("2.0.1"):
        get_func(orig_torrent, client_func)(ratio_limit=5, seeding_time_limit=100)
        check(lambda: orig_torrent.info.max_ratio, 5)
        check(lambda: orig_torrent.info.max_seeding_time, 100)
    else:
        with pytest.raises(NotImplementedError):
            get_func(orig_torrent, client_func)(ratio_limit=5, seeding_time_limit=100)


@pytest.mark.parametrize(
    "client_func",
    (("download_limit", "set_download_limit"), ("downloadLimit", "setDownloadLimit")),
)
def test_download_limit(orig_torrent, client_func):
    setattr(orig_torrent, client_func[0], 2048)
    check(lambda: get_func(orig_torrent, client_func[0]), 2048)
    check(lambda: orig_torrent.info.dl_limit, 2048)

    get_func(orig_torrent, client_func[1])(4096)
    check(lambda: get_func(orig_torrent, client_func[0]), 4096)
    check(lambda: orig_torrent.info.dl_limit, 4096)


@pytest.mark.parametrize(
    "client_func",
    (("upload_limit", "set_upload_limit"), ("uploadLimit", "setUploadLimit")),
)
def test_upload_limit(orig_torrent, client_func):
    setattr(orig_torrent, client_func[0], 2048)
    check(lambda: get_func(orig_torrent, client_func[0]), 2048)
    check(lambda: orig_torrent.info.up_limit, 2048)

    get_func(orig_torrent, client_func[1])(4096)
    check(lambda: get_func(orig_torrent, client_func[0]), 4096)
    check(lambda: orig_torrent.info.up_limit, 4096)


@pytest.mark.parametrize("client_func", ("set_location", "setLocation"))
def test_set_location(api_version, new_torrent, client_func):
    if v(api_version) >= v("2.0.2"):
        exp = None
        for attempt in range(2):
            try:
                loc = mkpath("/tmp", "3")
                get_func(new_torrent, client_func)(loc)
                check(
                    lambda: mkpath(new_torrent.info.save_path),
                    mkpath(loc),
                    any=True,
                )
                break
            except AssertionError as e:
                exp = e
        if exp:
            raise exp


@pytest.mark.parametrize("client_func", ("set_save_path", "setSavePath"))
def test_set_save_path(api_version, new_torrent, client_func):
    if v(api_version) >= v("2.8.4"):
        exp = None
        for attempt in range(2):
            try:
                loc = mkpath("/tmp", "savepath3")
                get_func(new_torrent, client_func)(loc)
                # qBittorrent may return trailing separators depending on version....
                check(
                    lambda: mkpath(new_torrent.info.save_path),
                    mkpath(loc),
                    any=True,
                )
                break
            except AssertionError as e:
                exp = e
        if exp:
            raise exp


@pytest.mark.parametrize("client_func", ("set_download_path", "setDownloadPath"))
def test_set_download_path(api_version, new_torrent, client_func):
    if v(api_version) >= v("2.8.4"):
        exp = None
        for attempt in range(2):
            try:
                loc = mkpath("/tmp", "downloadpath3")
                get_func(new_torrent, client_func)(loc)
                # qBittorrent may return trailing separators depending on version....
                check(
                    lambda: mkpath(new_torrent.info.download_path),
                    mkpath(loc),
                    any=True,
                )
                break
            except AssertionError as e:
                exp = e
        if exp:
            raise exp


@pytest.mark.parametrize("client_func", ("set_category", "setCategory"))
@pytest.mark.parametrize("category", ("category 1", "category_1"))
def test_set_category(client, orig_torrent, client_func, category):
    client.torrents_create_category(category=category)
    get_func(orig_torrent, client_func)(category=category)
    check(lambda: orig_torrent.info.category.replace("+", " "), category, reverse=True)
    client.torrents_remove_categories(categories=category)


@pytest.mark.parametrize("client_func", ("set_auto_management", "setAutoManagement"))
def test_set_auto_management(orig_torrent, client_func):
    current_setting = orig_torrent.auto_tmm
    get_func(orig_torrent, client_func)(enable=(not current_setting))
    check(lambda: orig_torrent.info.auto_tmm, not current_setting)
    get_func(orig_torrent, client_func)(enable=current_setting)
    check(lambda: orig_torrent.info.auto_tmm, current_setting)


@pytest.mark.parametrize(
    "client_func", ("toggle_sequential_download", "toggleSequentialDownload")
)
def test_toggle_sequential_download(orig_torrent, client_func):
    current_setting = orig_torrent.seq_dl
    get_func(orig_torrent, client_func)()
    check(lambda: orig_torrent.info.seq_dl, not current_setting)
    get_func(orig_torrent, client_func)()
    check(lambda: orig_torrent.info.seq_dl, current_setting)


@pytest.mark.parametrize(
    "client_func", ("toggle_first_last_piece_priority", "toggleFirstLastPiecePrio")
)
def test_toggle_first_last_piece_priority(api_version, orig_torrent, client_func):
    if v(api_version) >= v("2.0.2"):
        current_setting = orig_torrent.f_l_piece_prio
        get_func(orig_torrent, client_func)()
        sleep(1)
        check(lambda: orig_torrent.info.f_l_piece_prio, not current_setting)


@pytest.mark.parametrize("client_func", ("set_force_start", "setForceStart"))
def test_set_force_start(orig_torrent, client_func):
    current_setting = orig_torrent.force_start
    get_func(orig_torrent, client_func)(enable=(not current_setting))
    check(lambda: orig_torrent.info.force_start, not current_setting)
    get_func(orig_torrent, client_func)(enable=current_setting)
    check(lambda: orig_torrent.info.force_start, current_setting)


@pytest.mark.parametrize("client_func", ("set_super_seeding", "setSuperSeeding"))
def test_set_super_seeding(orig_torrent, client_func):
    current_setting = orig_torrent.super_seeding
    get_func(orig_torrent, client_func)(enable=(not current_setting))
    check(lambda: orig_torrent.info.super_seeding, not current_setting)
    get_func(orig_torrent, client_func)(enable=current_setting)
    check(lambda: orig_torrent.info.super_seeding, current_setting)


def test_properties(orig_torrent):
    assert isinstance(orig_torrent.properties, TorrentPropertiesDictionary)
    assert "save_path" in orig_torrent.properties


@pytest.mark.parametrize("trackers", ("127.0.0.2", ("127.0.0.3", "127.0.0.4")))
def test_trackers(orig_torrent, trackers):
    assert isinstance(orig_torrent.trackers, TrackersList)
    assert "num_peers" in orig_torrent.trackers[-1]

    orig_torrent.trackers = trackers
    check(lambda: (t.url for t in orig_torrent.trackers), trackers, reverse=True)


@pytest.mark.parametrize("client_func", ("add_trackers", "addTrackers"))
@pytest.mark.parametrize("trackers", ("127.0.0.2", ("127.0.0.3", "127.0.0.4")))
def test_add_tracker(new_torrent, client_func, trackers):
    get_func(new_torrent, client_func)(urls=trackers)
    sleep(0.5)  # try to stop crashing qbittorrent
    check(lambda: (t.url for t in new_torrent.trackers), trackers, reverse=True)


@pytest.mark.parametrize("client_func", ("edit_tracker", "editTracker"))
def test_edit_tracker(api_version, orig_torrent, client_func):
    if v(api_version) >= v("2.2.0"):
        orig_torrent.add_trackers(urls="127.0.1.1")
        get_func(orig_torrent, client_func)(orig_url="127.0.1.1", new_url="127.0.1.2")
        check(
            lambda: (t.url for t in orig_torrent.trackers),
            "127.0.1.1",
            reverse=True,
            negate=True,
        )
        check(lambda: (t.url for t in orig_torrent.trackers), "127.0.1.2", reverse=True)
        get_func(orig_torrent, "remove_trackers")(urls="127.0.1.2")
    else:
        with pytest.raises(NotImplementedError):
            get_func(orig_torrent, client_func)(
                orig_url="127.0.1.1", new_url="127.0.1.2"
            )


@pytest.mark.parametrize("client_func", ("remove_trackers", "removeTrackers"))
@pytest.mark.parametrize("trackers", ("127.0.2.2", ("127.0.2.3", "127.0.2.4")))
def test_remove_trackers(api_version, orig_torrent, client_func, trackers):
    if v(api_version) >= v("2.2.0"):
        check(
            lambda: (t.url for t in orig_torrent.trackers),
            trackers,
            reverse=True,
            negate=True,
        )
        orig_torrent.add_trackers(urls=trackers)
        check(lambda: (t.url for t in orig_torrent.trackers), trackers, reverse=True)
        get_func(orig_torrent, client_func)(urls=trackers)
        check(
            lambda: (t.url for t in orig_torrent.trackers),
            trackers,
            reverse=True,
            negate=True,
        )
    else:
        with pytest.raises(NotImplementedError):
            get_func(orig_torrent, client_func)(urls=trackers)


def test_webseeds(orig_torrent):
    assert isinstance(orig_torrent.webseeds, WebSeedsList)


def test_files(orig_torrent):
    assert isinstance(orig_torrent.files, TorrentFilesList)
    assert "id" in orig_torrent.files[0]


def test_recheck(orig_torrent):
    orig_torrent.recheck()


def test_reannounce(api_version, orig_torrent):
    if v(api_version) >= v("2.0.2"):
        orig_torrent.reannounce()
    else:
        with pytest.raises(NotImplementedError):
            orig_torrent.reannounce()


@pytest.mark.parametrize("client_func", ("rename_file", "renameFile"))
@pytest.mark.parametrize("name", ("new_name", "new name"))
def test_rename_file(api_version, app_version, new_torrent, client_func, name):
    sleep(1)
    if v(api_version) >= v("2.4.0"):
        get_func(new_torrent, client_func)(file_id=0, new_file_name=name)
        check(lambda: new_torrent.files[0].name, name)
    else:
        with pytest.raises(NotImplementedError):
            get_func(new_torrent, client_func)(file_id=0, new_file_name=name)

    if v(app_version) >= v("v4.3.3"):
        curr_name = new_torrent.files[0].name
        new_name = "NEW_" + name
        get_func(new_torrent, client_func)(old_path=curr_name, new_path=new_name)
        check(lambda: new_torrent.files[0].name, new_name)


@pytest.mark.parametrize("client_func", ("rename_folder", "renameFolder"))
@pytest.mark.parametrize("name", ("new_name", "new name"))
def test_rename_folder(api_version, app_version, new_torrent, client_func, name):
    # need to ensure we're at least on v4.3.3 to run test since
    # both v4.3.2 and v4.3.2 both use Web API 2.7
    if v(api_version) >= v("2.7") and v(app_version) >= v("v4.3.3"):
        # move the file in to a new folder
        orig_file_path = new_torrent.files[0].name
        new_folder = "qwer"
        new_torrent.rename_file(
            old_path=orig_file_path,
            new_path=new_folder + "/" + orig_file_path,
        )
        sleep(1)  # qBittorrent crashes if you make these calls too fast...
        # test rename that new folder
        get_func(new_torrent, client_func)(
            old_path=new_folder,
            new_path=name,
        )
        check(
            lambda: new_torrent.files[0].name.replace("+", " "),
            name + "/" + orig_file_path,
        )
    else:
        with pytest.raises(NotImplementedError):
            get_func(new_torrent, client_func)(old_path="", new_path="")


def test_export(api_version, orig_torrent):
    if v(api_version) >= v("2.8.14"):
        assert isinstance(orig_torrent.export(), bytes)
    else:
        with pytest.raises(NotImplementedError):
            orig_torrent.export()


@pytest.mark.parametrize("client_func", ("piece_states", "pieceStates"))
def test_piece_states(orig_torrent, client_func):
    assert isinstance(get_func(orig_torrent, client_func), TorrentPieceInfoList)


@pytest.mark.parametrize("client_func", ("piece_hashes", "pieceHashes"))
def test_piece_hashes(orig_torrent, client_func):
    assert isinstance(get_func(orig_torrent, client_func), TorrentPieceInfoList)


@pytest.mark.parametrize("client_func", ("file_priority", "filePriority"))
def test_file_priority(orig_torrent, client_func):
    get_func(orig_torrent, client_func)(file_ids=0, priority=7)
    check(lambda: orig_torrent.files[0].priority, 7)


@pytest.mark.parametrize("name", ("new_name", "new name"))
def test_rename(orig_torrent, name):
    orig_torrent.rename(new_name=name)
    check(lambda: orig_torrent.info.name.replace("+", " "), name)


@pytest.mark.parametrize(
    "client_func", (("add_tags", "remove_tags"), ("addTags", "removeTags"))
)
@pytest.mark.parametrize("tags", ("tag 1", ("tag 2", "tag 3")))
def test_add_remove_tags(client, api_version, orig_torrent, client_func, tags):
    if v(api_version) >= v("2.3.0"):
        get_func(orig_torrent, client_func[0])(tags=tags)
        check(lambda: orig_torrent.info.tags, tags, reverse=True)

        get_func(orig_torrent, client_func[1])(tags=tags)
        check(lambda: orig_torrent.info.tags, tags, reverse=True, negate=True)

        client.torrents_delete_tags(tags=tags)
    else:
        with pytest.raises(NotImplementedError):
            get_func(orig_torrent, client_func[0])(tags=tags)
        with pytest.raises(NotImplementedError):
            get_func(orig_torrent, client_func[1])(tags=tags)
