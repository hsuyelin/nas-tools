from sys import version_info

import pytest

from qbittorrentapi import Version
from tests.conftest import IS_QBT_DEV
from tests.conftest import api_version_map


@pytest.mark.skipif(IS_QBT_DEV, reason="testing devel version of qBittorrent")
def test_supported_versions(app_version, api_version):
    assert isinstance(Version.supported_api_versions(), set)
    assert api_version in Version.supported_api_versions()
    assert isinstance(Version.supported_app_versions(), set)
    assert app_version in Version.supported_app_versions()


@pytest.mark.skipif(IS_QBT_DEV, reason="testing devel version of qBittorrent")
def test_is_supported(app_version, api_version):
    assert Version.is_app_version_supported(app_version) is True
    assert Version.is_app_version_supported(app_version[1:]) is True
    assert Version.is_app_version_supported("0.0.0") is False

    assert Version.is_api_version_supported(api_version) is True
    assert Version.is_api_version_supported("v" + api_version) is True
    assert Version.is_api_version_supported("0.0.0") is False


@pytest.mark.skipif(IS_QBT_DEV, reason="testing devel version of qBittorrent")
def test_latest_version():
    # order of dictionary keys was guaranteed starting in python 3.7
    if version_info >= (3, 7):
        expected_latest_api_version = list(api_version_map.values())[-1]
        expected_latest_app_version = list(api_version_map.keys())[-1]
        assert Version.latest_supported_api_version() == expected_latest_api_version
        assert Version.latest_supported_app_version() == expected_latest_app_version
