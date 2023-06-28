import pytest

from qbittorrentapi._version_support import v
from qbittorrentapi.transfer import TransferInfoDictionary


def test_info(client):
    info = client.transfer_info()
    assert isinstance(info, TransferInfoDictionary)
    assert "connection_status" in info
    info = client.transfer.info
    assert isinstance(info, TransferInfoDictionary)
    assert "connection_status" in info


def test_speed_limits_mode(client):
    assert client.transfer_speed_limits_mode() in {"0", "1"}
    assert client.transfer.speed_limits_mode in {"0", "1"}

    original_mode = client.transfer.speed_limits_mode
    client.transfer_set_speed_limits_mode()
    assert client.transfer.speed_limits_mode != original_mode
    original_mode = client.transfer.speed_limits_mode
    client.transfer.set_speed_limits_mode()
    assert client.transfer.speed_limits_mode != original_mode

    original_mode = client.transfer.speed_limits_mode
    client.transfer_toggle_speed_limits_mode()
    assert client.transfer.speed_limits_mode != original_mode
    client.transfer_toggle_speed_limits_mode()
    assert client.transfer.speed_limits_mode == original_mode
    original_mode = client.transfer.speed_limits_mode
    client.transfer.toggle_speed_limits_mode()
    assert client.transfer.speed_limits_mode != original_mode
    client.transfer.toggle_speed_limits_mode()
    assert client.transfer.speed_limits_mode == original_mode

    client.transfer_set_speed_limits_mode(intended_state=True)
    assert client.transfer.speed_limits_mode != "0"
    client.transfer_setSpeedLimitsMode(intended_state=False)
    assert client.transfer.speed_limits_mode != "1"

    client.transfer_toggle_speed_limits_mode(intended_state=True)
    assert client.transfer.speed_limits_mode != "0"
    client.transfer_toggle_speed_limits_mode(intended_state=False)
    assert client.transfer.speed_limits_mode != "1"

    client.transfer.speed_limits_mode = True
    assert client.transfer.speed_limits_mode != "0"
    client.transfer.speed_limits_mode = False
    assert client.transfer.speed_limits_mode != "1"

    client.transfer.speedLimitsMode = True
    assert client.transfer.speedLimitsMode != "0"
    client.transfer.speedLimitsMode = False
    assert client.transfer.speedLimitsMode != "1"


def test_download_limit(client):
    client.transfer_set_download_limit(limit=2048)
    assert client.transfer_download_limit() == 2048
    client.transfer_setDownloadLimit(limit=3072)
    assert client.transfer_downloadLimit() == 3072

    client.transfer.download_limit = 4096
    assert client.transfer.download_limit == 4096
    client.transfer.downloadLimit = 5120
    assert client.transfer.downloadLimit == 5120


def test_upload_limit(client):
    client.transfer_set_upload_limit(limit=2048)
    assert client.transfer_upload_limit() == 2048
    client.transfer_setUploadLimit(limit=3072)
    assert client.transfer_uploadLimit() == 3072

    client.transfer.upload_limit = 4096
    assert client.transfer.upload_limit == 4096
    client.transfer.uploadLimit = 5120
    assert client.transfer.uploadLimit == 5120


def test_ban_peers(client, api_version):
    if v(api_version) >= v("2.3"):
        client.transfer_ban_peers(peers="1.1.1.1:8080")
        assert "1.1.1.1" in client.app.preferences.banned_IPs
        client.transfer.ban_peers(peers="1.1.1.2:8080")
        assert "1.1.1.2" in client.app.preferences.banned_IPs

        client.transfer_ban_peers(peers=["1.1.1.3:8080", "1.1.1.4:8080"])
        assert "1.1.1.3" in client.app.preferences.banned_IPs
        assert "1.1.1.4" in client.app.preferences.banned_IPs
        client.transfer.ban_peers(peers=["1.1.1.5:8080", "1.1.1.6:8080"])
        assert "1.1.1.5" in client.app.preferences.banned_IPs
        assert "1.1.1.6" in client.app.preferences.banned_IPs
    else:
        with pytest.raises(NotImplementedError):
            client.transfer_ban_peers(peers="1.1.1.1:8080")
