import pytest

from qbittorrentapi._attrdict import AttrDict
from tests.conftest import IS_QBT_DEV


def test_version(client, app_version):
    assert client.app_version() == app_version
    assert client.app.version == app_version
    assert client.application.version == app_version


@pytest.mark.skipif(IS_QBT_DEV, reason="testing devel version of qBittorrent")
def test_web_api_version(client, api_version):
    assert client.app_web_api_version() == api_version
    assert client.app.web_api_version == api_version
    assert client.application.web_api_version == api_version


@pytest.mark.skipif_before_api_version("2.3")
def test_build_info(client):
    assert "libtorrent" in client.app_build_info()
    assert "libtorrent" in client.app.build_info


@pytest.mark.skipif_after_api_version("2.3")
def test_build_info_not_implemented(client):
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
