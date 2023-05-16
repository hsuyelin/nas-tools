# -*- coding: utf-8 -*-
from plexapi.exceptions import BadRequest
from plexapi.playqueue import PlayQueue
import pytest


def test_create_playqueue(plex, show):
    # create the playlist
    episodes = show.episodes()
    pq = plex.createPlayQueue(episodes[:3])
    assert len(pq) == 3, "PlayQueue does not contain 3 items."
    assert pq.playQueueLastAddedItemID is None
    assert pq.playQueueSelectedMetadataItemID == episodes[0].ratingKey
    assert (
        pq.items[0].ratingKey == episodes[0].ratingKey
    ), "Items not in proper order [0a]."
    assert (
        pq.items[1].ratingKey == episodes[1].ratingKey
    ), "Items not in proper order [1a]."
    assert (
        pq.items[2].ratingKey == episodes[2].ratingKey
    ), "Items not in proper order [2a]."

    # Test move items around (b)
    pq.moveItem(pq.items[1])
    assert pq.playQueueLastAddedItemID is None
    assert pq.playQueueSelectedMetadataItemID == episodes[0].ratingKey
    assert (
        pq.items[0].ratingKey == episodes[1].ratingKey
    ), "Items not in proper order [0b]."
    assert (
        pq.items[1].ratingKey == episodes[0].ratingKey
    ), "Items not in proper order [1b]."
    assert (
        pq.items[2].ratingKey == episodes[2].ratingKey
    ), "Items not in proper order [2b]."

    # Test move items around (c)
    pq.moveItem(pq.items[0], after=pq.items[1])
    assert pq.playQueueLastAddedItemID == pq.items[1].playQueueItemID
    assert pq.playQueueSelectedMetadataItemID == episodes[0].ratingKey
    assert (
        pq.items[0].ratingKey == episodes[0].ratingKey
    ), "Items not in proper order [0c]."
    assert (
        pq.items[1].ratingKey == episodes[1].ratingKey
    ), "Items not in proper order [1c]."
    assert (
        pq.items[2].ratingKey == episodes[2].ratingKey
    ), "Items not in proper order [2c]."

    # Test adding an item to Up Next section
    pq.addItem(episodes[3])
    assert pq.playQueueLastAddedItemID == pq.items[2].playQueueItemID
    assert pq.playQueueSelectedMetadataItemID == episodes[0].ratingKey
    assert pq.items[2].ratingKey == episodes[3].ratingKey, (
        f"Missing added item: {episodes[3]}"
    )

    # Test adding an item to play next
    pq.addItem(episodes[4], playNext=True)
    assert pq.playQueueLastAddedItemID == pq.items[3].playQueueItemID
    assert pq.playQueueSelectedMetadataItemID == episodes[0].ratingKey
    assert pq.items[1].ratingKey == episodes[4].ratingKey, (
        f"Missing added item: {episodes[4]}"
    )

    # Test add another item into Up Next section
    pq.addItem(episodes[5])
    assert pq.playQueueLastAddedItemID == pq.items[4].playQueueItemID
    assert pq.playQueueSelectedMetadataItemID == episodes[0].ratingKey
    assert pq.items[4].ratingKey == episodes[5].ratingKey, (
        f"Missing added item: {episodes[5]}"
    )

    # Test removing an item
    toremove = pq.items[3]
    pq.removeItem(toremove)
    assert pq.playQueueLastAddedItemID == pq.items[3].playQueueItemID
    assert pq.playQueueSelectedMetadataItemID == episodes[0].ratingKey
    assert toremove not in pq, f"Removed item still in PlayQueue: {toremove}"
    assert len(pq) == 5, f"PlayQueue should have 5 items, {len(pq)} found"

    # Test clearing the PlayQueue
    pq.clear()
    assert pq.playQueueSelectedMetadataItemID == episodes[0].ratingKey
    assert len(pq) == 1, f"PlayQueue should have 1 item, {len(pq)} found"

    # Test adding an item again
    pq.addItem(episodes[7])
    assert pq.playQueueLastAddedItemID == pq.items[1].playQueueItemID
    assert pq.playQueueSelectedMetadataItemID == episodes[0].ratingKey
    assert pq.items[1].ratingKey == episodes[7].ratingKey, (
        f"Missing added item: {episodes[7]}"
    )


def test_create_playqueue_with_single_item(plex, movie):
    pq = plex.createPlayQueue(movie)
    assert len(pq) == 1
    assert pq.items[0].ratingKey == movie.ratingKey


def test_create_playqueue_with_start_choice(plex, show):
    episodes = show.episodes()
    pq = plex.createPlayQueue(episodes[:3], startItem=episodes[1])
    assert pq.playQueueSelectedMetadataItemID == pq.items[1].ratingKey


def test_modify_playqueue_with_library_media(plex, show):
    episodes = show.episodes()
    pq = plex.createPlayQueue(episodes[:3])
    assert len(pq) == 3, "PlayQueue does not contain 3 items."
    # Test move PlayQueue using library items
    pq.moveItem(episodes[1], after=episodes[2])
    assert pq.items[0].ratingKey == episodes[0].ratingKey, "Items not in proper order."
    assert pq.items[2].ratingKey == episodes[1].ratingKey, "Items not in proper order."
    assert pq.items[1].ratingKey == episodes[2].ratingKey, "Items not in proper order."
    # Test too many matching library items
    pq.addItem(episodes[0])
    pq.addItem(episodes[0])
    with pytest.raises(BadRequest):
        pq.moveItem(episodes[2], after=episodes[0])
    # Test items not in PlayQueue
    with pytest.raises(BadRequest):
        pq.moveItem(episodes[9], after=episodes[0])
    with pytest.raises(BadRequest):
        pq.removeItem(episodes[9])


def test_create_playqueue_from_playlist(plex, album):
    try:
        playlist = plex.createPlaylist("test_playlist", items=album)
        pq = playlist.playQueue(shuffle=1)
        assert pq.playQueueShuffled is True
        assert len(pq) == len(playlist)
        pq.addItem(playlist)
        assert len(pq) == 2 * len(playlist)
    finally:
        playlist.delete()


def test_create_playqueue_from_collection(plex, music, album):
    try:
        collection = plex.createCollection("test_collection", music, album)
        pq = collection.playQueue(shuffle=1)
        assert pq.playQueueShuffled is True
        assert len(pq) == len(album.tracks())
        pq.addItem(collection.items()[0])
        assert len(pq) == len(collection) + 1
    finally:
        collection.delete()


def test_lookup_playqueue(plex, movie):
    pq = PlayQueue.create(plex, movie)
    pq_id = pq.playQueueID
    pq2 = PlayQueue.get(plex, pq_id)
    assert pq.playQueueID == pq2.playQueueID
    assert pq.items == pq2.items
