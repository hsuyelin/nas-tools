import pytest

from qbittorrentapi.sync import SyncMainDataDictionary
from qbittorrentapi.sync import SyncTorrentPeersDictionary


@pytest.mark.parametrize("rid", (None, 0, 1, 100000))
def test_maindata1(client, rid):
    assert isinstance(client.sync_maindata(rid=rid), SyncMainDataDictionary)


@pytest.mark.parametrize("rid", (None, 0, 1, 100000))
def test_maindata2(client, rid):
    assert isinstance(client.sync.maindata(rid=rid), SyncMainDataDictionary)
    assert isinstance(client.sync.maindata.delta(), SyncMainDataDictionary)
    assert isinstance(client.sync.maindata.delta(), SyncMainDataDictionary)


def test_maindata3(client):
    client.sync.maindata()
    assert client.sync.maindata._rid != 0
    client.sync.maindata.reset_rid()
    assert client.sync.maindata._rid == 0


@pytest.mark.parametrize("rid", (None, 0, 1, 100000))
def test_torrent_peers(client, rid, orig_torrent):
    assert isinstance(
        client.sync_torrent_peers(rid=rid, torrent_hash=orig_torrent.hash),
        SyncTorrentPeersDictionary,
    )
    assert isinstance(
        client.sync.torrent_peers(rid=rid, torrent_hash=orig_torrent.hash),
        SyncTorrentPeersDictionary,
    )

    assert isinstance(
        client.sync.torrent_peers.delta(torrent_hash=orig_torrent.hash),
        SyncTorrentPeersDictionary,
    )

    client.sync.torrent_peers.reset_rid()
    assert client.sync.torrent_peers._rid == 0
