import os
import secrets

import dotenv
import pytest

from transmission_rpc import LOGGER
from transmission_rpc.client import Client

dotenv.load_dotenv()

HOST = os.getenv("TR_HOST", "127.0.0.1")
PORT = int(os.getenv("TR_PORT", "9091"))
USER = os.getenv("TR_USER", "admin")
PASSWORD = os.getenv("TR_PASSWORD", "password")


@pytest.fixture()
def tr_client():
    LOGGER.setLevel("INFO")
    with Client(host=HOST, port=PORT, username=USER, password=PASSWORD) as c:
        for torrent in c.get_torrents():
            c.remove_torrent(torrent.id, delete_data=True)
        yield c
        for torrent in c.get_torrents():
            c.remove_torrent(torrent.id, delete_data=True)


@pytest.fixture()
def fake_hash_factory():
    return lambda: secrets.token_hex(20)
