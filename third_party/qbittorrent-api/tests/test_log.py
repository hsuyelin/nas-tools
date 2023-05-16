import pytest

from qbittorrentapi.log import LogMainList
from qbittorrentapi.log import LogPeersList


@pytest.mark.parametrize("normal", (True, False))
@pytest.mark.parametrize("info", (True, False))
@pytest.mark.parametrize("warning", (True, False))
@pytest.mark.parametrize("critical", (True, False))
@pytest.mark.parametrize("last_known_id", (None, 0, 100000))
def test_main(client, normal, info, warning, critical, last_known_id):
    assert isinstance(
        client.log_main(
            normal=normal,
            info=info,
            warning=warning,
            critical=critical,
            last_known_id=last_known_id,
        ),
        LogMainList,
    )
    assert isinstance(
        client.log.main(
            normal=normal,
            info=info,
            warning=warning,
            critical=critical,
            last_known_id=last_known_id,
        ),
        LogMainList,
    )
    assert isinstance(client.log.main.info(last_known_id=last_known_id), LogMainList)
    assert isinstance(client.log.main.normal(last_known_id=last_known_id), LogMainList)
    assert isinstance(client.log.main.warning(last_known_id=last_known_id), LogMainList)
    assert isinstance(
        client.log.main.critical(last_known_id=last_known_id), LogMainList
    )


@pytest.mark.parametrize("last_known_id", (None, 0, 100000))
def test_log_peers(client, last_known_id):
    assert isinstance(client.log_peers(last_known_id=last_known_id), LogPeersList)
    assert isinstance(client.log.peers(last_known_id=last_known_id), LogPeersList)
