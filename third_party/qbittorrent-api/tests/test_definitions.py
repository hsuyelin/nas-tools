from enum import Enum

import pytest

from qbittorrentapi._attrdict import AttrDict
from qbittorrentapi.definitions import Dictionary
from qbittorrentapi.definitions import List
from qbittorrentapi.definitions import ListEntry
from qbittorrentapi.definitions import TorrentStates

all_states = (
    "error",
    "missingFiles",
    "uploading",
    "pausedUP",
    "queuedUP",
    "stalledUP",
    "checkingUP",
    "forcedUP",
    "allocating",
    "downloading",
    "metaDL",
    "forcedMetaDL",
    "pausedDL",
    "queuedDL",
    "forcedDL",
    "stalledDL",
    "checkingDL",
    "checkingResumeData",
    "moving",
    "unknown",
)

downloading_states = (
    "downloading",
    "metaDL",
    "forcedMetaDL",
    "stalledDL",
    "checkingDL",
    "pausedDL",
    "queuedDL",
    "forcedDL",
)

uploading_states = ("uploading", "stalledUP", "checkingUP", "queuedUP", "forcedUP")

complete_states = (
    "uploading",
    "stalledUP",
    "checkingUP",
    "pausedUP",
    "queuedUP",
    "forcedUP",
)

checking_states = ("checkingUP", "checkingDL", "checkingResumeData")

errored_states = ("missingFiles", "error")

paused_states = ("pausedUP", "pausedDL")


def test_torrent_states_exists():
    assert isinstance(TorrentStates("unknown"), Enum)


@pytest.mark.parametrize("state", all_states)
def test_all_states(state):
    assert TorrentStates(state) in TorrentStates


@pytest.mark.parametrize("state", downloading_states)
def test_downloading_states(state):
    assert TorrentStates(state).is_downloading


@pytest.mark.parametrize("state", uploading_states)
def test_uploading_states(state):
    assert TorrentStates(state).is_uploading


@pytest.mark.parametrize("state", complete_states)
def test_completing_states(state):
    assert TorrentStates(state).is_complete


@pytest.mark.parametrize("state", checking_states)
def test_checking_states(state):
    assert TorrentStates(state).is_checking


@pytest.mark.parametrize("state", errored_states)
def test_errored_states(state):
    assert TorrentStates(state).is_errored


@pytest.mark.parametrize("state", paused_states)
def test_paused_states(state):
    assert TorrentStates(state).is_paused


def test_testing_groups():
    assert set(all_states) == {s.value for s in iter(TorrentStates)}
    assert set(downloading_states) == {
        s.value for s in TorrentStates if s.is_downloading
    }
    assert set(uploading_states) == {s.value for s in TorrentStates if s.is_uploading}
    assert set(complete_states) == {s.value for s in TorrentStates if s.is_complete}
    assert set(checking_states) == {s.value for s in TorrentStates if s.is_checking}
    assert set(errored_states) == {s.value for s in TorrentStates if s.is_errored}


def test_dictionary():
    assert len(Dictionary()) == 0
    assert len(Dictionary({"one": {"two": 2}})) == 1
    assert isinstance(Dictionary({"one": {"two": 2}}).one, AttrDict)
    assert isinstance(Dictionary({"one": {"two": 2}})["one"], AttrDict)
    assert Dictionary({"one": {"two": 2}}).one.two == 2
    assert Dictionary({"one": {"two": 2}})["one"]["two"] == 2
    assert Dictionary({"three": 3}).three == 3
    assert Dictionary({"three": 3})["three"] == 3


def test_list():
    assert len(List()) == 0
    list_entries = ({"one": "1"}, {"two": "2"}, {"three": "3"})
    test_list = List(list_entries=list_entries, entry_class=ListEntry)
    assert len(test_list) == 3
    assert issubclass(type(test_list[0]), ListEntry)
    assert test_list[0].one == "1"
