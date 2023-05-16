import logging

import pytest

from qbittorrentapi import Client
from qbittorrentapi.decorators import endpoint_introduced
from qbittorrentapi.decorators import handle_hashes
from qbittorrentapi.decorators import version_removed
from qbittorrentapi.request import Request

list2str = Request._list2string


def test_login_required(caplog, app_version):
    client = Client(
        RAISE_NOTIMPLEMENTEDERROR_FOR_UNIMPLEMENTED_API_ENDPOINTS=True,
        VERIFY_WEBUI_CERTIFICATE=False,
    )
    # check if first API call works if already logged in
    client.auth_log_in()
    with caplog.at_level(logging.DEBUG, logger="qbittorrentapi"):
        qbt_version = client.app.version
    assert "Login may have expired...attempting new login" not in caplog.text
    assert qbt_version == app_version

    # ensure login happens after first API call fails
    client.auth_log_out()
    with caplog.at_level(logging.DEBUG, logger="qbittorrentapi"):
        qbt_version = client.app.version
    assert "Login may have expired...attempting new login" in caplog.text
    assert qbt_version == app_version


@pytest.mark.parametrize("test_hash", (None, "", "xcvbxcvbxcvb"))
@pytest.mark.parametrize("other_param", (None, "", "irivgjkd"))
def test_hash_handler_single_hash(test_hash, other_param):
    class FakeClient:
        @handle_hashes
        def single_torrent_func(self, torrent_hash=None, param=None):
            assert torrent_hash == test_hash
            assert param == other_param

    FakeClient().single_torrent_func(test_hash, other_param)
    FakeClient().single_torrent_func(test_hash, param=other_param)
    FakeClient().single_torrent_func(hash=test_hash, param=other_param)
    FakeClient().single_torrent_func(torrent_hash=test_hash, param=other_param)


@pytest.mark.parametrize(
    "test_hashes", (None, "", "xcvbxcvbxcvb", ("xcvbxcvbxcvb", "ertyertye"))
)
@pytest.mark.parametrize("other_param", (None, "", "irivgjkd"))
def test_hash_handler_multiple_hashes(test_hashes, other_param):
    class FakeClient:
        @handle_hashes
        def multiple_torrent_func(self, torrent_hashes=None, param=None):
            assert list2str(torrent_hashes) == list2str(test_hashes)
            assert param == other_param

    FakeClient().multiple_torrent_func(test_hashes, other_param)
    FakeClient().multiple_torrent_func(test_hashes, param=other_param)
    FakeClient().multiple_torrent_func(hashes=test_hashes, param=other_param)
    FakeClient().multiple_torrent_func(torrent_hashes=test_hashes, param=other_param)


def test_version_implemented():
    class FakeClient:
        _RAISE_UNIMPLEMENTEDERROR_FOR_UNIMPLEMENTED_API_ENDPOINTS = True
        version = "1.0"

        def app_web_api_version(self):
            return self.version

        @endpoint_introduced("1.1", "test1")
        def endpoint_not_implemented(self):
            return

        @endpoint_introduced("0.9", "test2")
        def endpoint_implemented(self):
            return

    with pytest.raises(NotImplementedError):
        FakeClient().endpoint_not_implemented()

    assert FakeClient().endpoint_implemented() is None

    fake_client = FakeClient()
    fake_client._RAISE_UNIMPLEMENTEDERROR_FOR_UNIMPLEMENTED_API_ENDPOINTS = False
    assert fake_client.endpoint_not_implemented() is None


def test_version_removed():
    class FakeClient:
        _RAISE_UNIMPLEMENTEDERROR_FOR_UNIMPLEMENTED_API_ENDPOINTS = True
        version = "1.0"

        def app_web_api_version(self):
            return self.version

        @version_removed("0.0.0", "test1")
        def endpoint_not_implemented(self):
            return

        @version_removed("9999999", "test2")
        def endpoint_implemented(self):
            return

    with pytest.raises(NotImplementedError):
        FakeClient().endpoint_not_implemented()

    assert FakeClient().endpoint_implemented() is None

    fake_client = FakeClient()
    fake_client._RAISE_UNIMPLEMENTEDERROR_FOR_UNIMPLEMENTED_API_ENDPOINTS = False
    assert fake_client.endpoint_not_implemented() is None
