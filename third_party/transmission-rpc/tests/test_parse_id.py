import pytest

from transmission_rpc.client import _parse_torrent_id, _parse_torrent_ids

example_hash = "51ba7d0dd45ab9b9564329c33f4f97493b677924"


@pytest.mark.parametrize("arg", [float(1), "non-hash-string"])
def test_parse_id_raise(arg):
    with pytest.raises(ValueError, match=f"{arg} is not valid torrent id"):
        _parse_torrent_id(arg)


@pytest.mark.parametrize(
    ("arg", "expected"),
    [
        ("recently-active", "recently-active"),
        (example_hash, [example_hash]),
        ((2, example_hash), [2, example_hash]),
        (3, [3]),
        (None, []),
    ],
)
def test_parse_torrent_ids(arg, expected):
    assert _parse_torrent_ids(arg) == expected, f"parse_torrent_ids({arg}) != {expected}"


@pytest.mark.parametrize("arg", ["not-recently-active", "non-hash-string", -1, 1.1, "5:10", "5,6,8,9,10"])
def test_parse_torrent_ids_value_error(arg):
    with pytest.raises(ValueError, match="torrent id"):
        _parse_torrent_ids(arg)
