from os import environ
from time import sleep

import pytest

from qbittorrentapi import APIConnectionError


def test_shutdown(client):
    if environ.get("CI") == "true":
        client.app.shutdown()
        with pytest.raises(APIConnectionError):
            for _ in range(100):
                client.app_version()
                sleep(0.1)
