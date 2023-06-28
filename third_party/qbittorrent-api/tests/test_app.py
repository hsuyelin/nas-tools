import pytest

from qbittorrentapi._attrdict import AttrDict
from qbittorrentapi._version_support import v
from tests.conftest import IS_QBT_DEV


def test_version(client, app_version):
    assert client.app_version() == app_version
    assert client.app.version == app_version
    assert client.application.version == app_version


def test_web_api_version(client, api_version):
    if IS_QBT_DEV:
        return

    assert client.app_web_api_version() == api_version
    assert client.app.web_api_version == api_version
    assert client.application.web_api_version == api_version


def test_build_info(client, api_version):
    if v(api_version) >= v("2.3"):
        assert "libtorrent" in client.app_build_info()
        assert "libtorrent" in client.app.build_info
    else:
        with pytest.raises(NotImplementedError):
            assert "libtorrent" in client.app_build_info()
        with pytest.raises(NotImplementedError):
            assert "libtorrent" in client.app.build_info


def test_preferences(client):
    prefs = client.app_preferences()
    assert "dht" in prefs
    assert "dht" in client.app.preferences
    dht = prefs["dht"]
    client.app.preferences = AttrDict(dht=(not dht))
    assert dht is not client.app.preferences.dht
    client.app_set_preferences(prefs=dict(dht=dht))
    assert dht is client.app.preferences.dht


def test_default_save_path(client):
    assert "download" in client.app_default_save_path().lower()
    assert "download" in client.app.default_save_path.lower()
