from time import sleep

import pytest

from qbittorrentapi import NotFound404Error
from qbittorrentapi._version_support import v
from qbittorrentapi.search import SearchJobDictionary
from qbittorrentapi.search import SearchResultsDictionary
from qbittorrentapi.search import SearchStatusesList
from tests.conftest import check
from tests.conftest import get_func

plugin_name = "legittorrents"
legit_torrents_url = "https://raw.githubusercontent.com/qbittorrent/search-plugins/master/nova3/engines/legittorrents.py"


@pytest.mark.parametrize(
    "client_func", ("search_update_plugins", "search.update_plugins")
)
def test_update_plugins(client, api_version, client_func):
    if v(api_version) >= v("2.1.1"):
        get_func(client, client_func)()
        check(
            lambda: any(
                entry["message"].startswith("Updating plugin ")
                or entry["message"] == "All plugins are already up to date."
                for entry in reversed(client.log.main())
            ),
            True,
        )
    else:
        with pytest.raises(NotImplementedError):
            client.search_update_plugins()


@pytest.mark.parametrize(
    "client_func",
    (
        ("search_plugins", "search_enable_plugin"),
        ("search.plugins", "search.enable_plugin"),
    ),
)
def test_enable_plugin(client, api_version, client_func):
    if v(api_version) >= v("2.1.1"):
        loop_limit = 3
        for loop_count in range(loop_limit):
            try:
                try:
                    plugins = get_func(client, client_func[0])()
                except TypeError:
                    plugins = get_func(client, client_func[0])
                get_func(client, client_func[1])(
                    plugins=(p["name"] for p in plugins), enable=False
                )
                check(
                    lambda: (p["enabled"] for p in client.search_plugins()),
                    True,
                    reverse=True,
                    negate=True,
                )
                get_func(client, client_func[1])(
                    plugins=(p["name"] for p in plugins), enable=True
                )
                check(
                    lambda: (p["enabled"] for p in client.search_plugins()),
                    False,
                    reverse=True,
                    negate=True,
                )
                break
            except Exception as e:
                if loop_count >= (loop_limit - 1):
                    raise e
    else:
        with pytest.raises(NotImplementedError):
            get_func(client, client_func[1])()


@pytest.mark.parametrize(
    "client_func",
    (
        ("search_install_plugin", "search_uninstall_plugin"),
        ("search.install_plugin", "search.uninstall_plugin"),
    ),
)
def test_install_uninstall_plugin(client, api_version, client_func):
    if v(api_version) >= v("2.1.1"):
        for _ in range(3):
            try:
                get_func(client, client_func[0])(sources=legit_torrents_url)
                check(
                    lambda: (p.name for p in client.search.plugins),
                    plugin_name,
                    reverse=True,
                )
                break
            except AssertionError:
                pass
        for _ in range(3):
            try:
                get_func(client, client_func[1])(names=plugin_name)
                check(
                    lambda: (p.name for p in client.search.plugins),
                    plugin_name,
                    reverse=True,
                    negate=True,
                )
            except AssertionError:
                pass
    else:
        with pytest.raises(NotImplementedError):
            client.search_install_plugin()
        with pytest.raises(NotImplementedError):
            client.search_uninstall_plugin()


@pytest.mark.parametrize("client_func", ("search_categories", "search.categories"))
def test_categories(client, api_version, client_func):
    if v("2.6") > v(api_version) >= v("2.1.1"):
        check(lambda: get_func(client, client_func)(), "All categories", reverse=True)
    else:
        with pytest.raises(NotImplementedError):
            get_func(client, client_func)()


@pytest.mark.parametrize(
    "client_func",
    (
        (
            "search_start",
            "search_status",
            "search_results",
            "search_stop",
            "search_delete",
        ),
        (
            "search.start",
            "search.status",
            "search.results",
            "search.stop",
            "search.delete",
        ),
    ),
)
def test_search(client, api_version, client_func):
    if v(api_version) >= v("2.1.1"):
        job = get_func(client, client_func[0])(
            pattern="Ubuntu", plugins="enabled", category="all"
        )
        assert isinstance(job, SearchJobDictionary)
        statuses = get_func(client, client_func[1])(search_id=job["id"])
        assert isinstance(statuses, SearchStatusesList)
        assert statuses[0]["status"] == "Running"
        results = get_func(client, client_func[2])(search_id=job["id"], limit=1)
        assert isinstance(results, SearchResultsDictionary)
        results = job.results()
        assert isinstance(results, SearchResultsDictionary)
        get_func(client, client_func[3])(search_id=job["id"])
        check(
            lambda: get_func(client, client_func[1])(search_id=job["id"])[0]["status"],
            "Stopped",
        )
        get_func(client, client_func[4])(search_id=job["id"])
        statuses = get_func(client, client_func[1])()
        assert not statuses
    else:
        with pytest.raises(NotImplementedError):
            get_func(client, client_func[0])()


@pytest.mark.parametrize(
    "client_func", (("search_stop", "search_start"), ("search.stop", "search.start"))
)
def test_stop(client, api_version, client_func):
    if v(api_version) >= v("2.1.1"):
        job = get_func(client, client_func[1])(
            pattern="Ubuntu", plugins="enabled", category="all"
        )
        sleep(1)
        get_func(client, client_func[0])(search_id=job.id)
        check(lambda: client.search.status(search_id=job["id"])[0]["status"], "Stopped")

        job = get_func(client, client_func[1])(
            pattern="Ubuntu", plugins="enabled", category="all"
        )
        sleep(1)
        job.stop()
        check(lambda: client.search.status(search_id=job["id"])[0]["status"], "Stopped")
    else:
        with pytest.raises(NotImplementedError):
            get_func(client, client_func[0])(search_id=100)


def test_delete(client, api_version):
    if v(api_version) >= v("2.1.1"):
        job = client.search_start(pattern="Ubuntu", plugins="enabled", category="all")
        job.delete()
        with pytest.raises(NotFound404Error):
            job.status()
    else:
        with pytest.raises(NotImplementedError):
            client.search_stop(search_id=100)
