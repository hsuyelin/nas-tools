from os import environ

import pytest

from tests.utils import check


@pytest.mark.skipif(environ.get("CI") != "true", reason="not in CI")
def test_shutdown(client):
    client.app.shutdown()
    with pytest.raises(AssertionError, match="qBittorrent crashed..."):
        check(lambda: client.app_version(), "")
