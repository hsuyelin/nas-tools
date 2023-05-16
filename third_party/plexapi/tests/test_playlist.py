# -*- coding: utf-8 -*-
import time
from urllib.parse import quote_plus

import pytest
from plexapi.exceptions import BadRequest, NotFound, Unsupported

from . import conftest as utils
from . import test_mixins


def test_Playlist_attrs(playlist):
    assert utils.is_datetime(playlist.addedAt)
    assert playlist.allowSync is True
    assert utils.is_composite(playlist.composite, prefix="/playlists")
    assert playlist.content is None
    assert utils.is_int(playlist.duration)
    assert playlist.durationInSeconds is None
    assert playlist.icon is None
    assert playlist.guid.startswith("com.plexapp.agents.none://")
    assert playlist.key.startswith("/playlists/")
    assert playlist.leafCount == 3
    assert playlist.playlistType == "video"
    assert utils.is_int(playlist.ratingKey)
    assert playlist.smart is False
    assert playlist.summary == ""
    assert playlist.title == "Test Playlist"
    assert playlist.type == "playlist"
    assert utils.is_datetime(playlist.updatedAt)
    assert playlist.thumb == playlist.composite
    assert playlist.metadataType == "movie"
    assert playlist.isVideo is True
    assert playlist.isAudio is False
    assert playlist.isPhoto is False


def test_Playlist_create(plex, show):
    # create the playlist
    title = 'test_create_playlist_show'
    episodes = show.episodes()
    playlist = plex.createPlaylist(title, items=episodes[:3])
    try:
        items = playlist.items()
        # Test create playlist
        assert playlist.title == title, 'Playlist not created successfully.'
        assert len(items) == 3, 'Playlist does not contain 3 items.'
        assert items[0].ratingKey == episodes[0].ratingKey, 'Items not in proper order [0a].'
        assert items[1].ratingKey == episodes[1].ratingKey, 'Items not in proper order [1a].'
        assert items[2].ratingKey == episodes[2].ratingKey, 'Items not in proper order [2a].'
        # Test move items around (b)
        playlist.moveItem(items[1])
        items = playlist.reload().items()
        assert items[0].ratingKey == episodes[1].ratingKey, 'Items not in proper order [0b].'
        assert items[1].ratingKey == episodes[0].ratingKey, 'Items not in proper order [1b].'
        assert items[2].ratingKey == episodes[2].ratingKey, 'Items not in proper order [2b].'
        # Test move items around (c)
        playlist.moveItem(items[0], items[1])
        items = playlist.reload().items()
        assert items[0].ratingKey == episodes[0].ratingKey, 'Items not in proper order [0c].'
        assert items[1].ratingKey == episodes[1].ratingKey, 'Items not in proper order [1c].'
        assert items[2].ratingKey == episodes[2].ratingKey, 'Items not in proper order [2c].'
        # Test add item
        playlist.addItems(episodes[3])
        items = playlist.reload().items()
        assert items[3].ratingKey == episodes[3].ratingKey, f'Missing added item: {episodes[3]}'
        # Test add two items
        playlist.addItems(episodes[4:6])
        items = playlist.reload().items()
        assert items[4].ratingKey == episodes[4].ratingKey, f'Missing added item: {episodes[4]}'
        assert items[5].ratingKey == episodes[5].ratingKey, f'Missing added item: {episodes[5]}'
        assert len(items) == 6, f'Playlist should have 6 items, {len(items)} found'
        # Test remove item
        toremove = items[5]
        playlist.removeItems(toremove)
        items = playlist.reload().items()
        assert toremove not in items, f'Removed item still in playlist: {items[5]}'
        assert len(items) == 5, f'Playlist should have 5 items, {len(items)} found'
        # Test remove two item
        toremove = items[3:5]
        playlist.removeItems(toremove)
        items = playlist.reload().items()
        assert toremove[0] not in items, f'Removed item still in playlist: {items[3]}'
        assert toremove[1] not in items, f'Removed item still in playlist: {items[4]}'
        assert len(items) == 3, f'Playlist should have 5 items, {len(items)} found'
    finally:
        playlist.delete()


def test_Playlist_edit(plex, movie):
    title = 'test_playlist_edit'
    new_title = 'test_playlist_edit_new_title'
    new_summary = 'test_playlist_edit_summary'
    try:
        playlist = plex.createPlaylist(title, items=movie)
        assert playlist.title == title
        assert playlist.summary == ''
        playlist.edit(title=new_title, summary=new_summary)
        playlist.reload()
        assert playlist.title == new_title
        assert playlist.summary == new_summary
    finally:
        playlist.delete()


def test_Playlist_item(plex, show):
    title = 'test_playlist_item'
    episodes = show.episodes()
    try:
        playlist = plex.createPlaylist(title, items=episodes[:3])
        item1 = playlist.item("Winter Is Coming")
        assert item1 in playlist.items()
        item2 = playlist.get("Winter Is Coming")
        assert item2 in playlist.items()
        assert item1 == item2
        with pytest.raises(NotFound):
            playlist.item("Does not exist")
    finally:
        playlist.delete()


@pytest.mark.client
def test_Playlist_play(plex, client, artist, album):
    try:
        playlist_name = 'test_play_playlist'
        playlist = plex.createPlaylist(playlist_name, items=album)
        client.playMedia(playlist); time.sleep(5)
        client.stop('music'); time.sleep(1)
    finally:
        playlist.delete()
    assert playlist_name not in [i.title for i in plex.playlists()]


def test_Playlist_photos(plex, photoalbum):
    album = photoalbum
    photos = album.photos()
    try:
        playlist_name = 'test_playlist_photos'
        playlist = plex.createPlaylist(playlist_name, items=photos)
        assert len(playlist.items()) >= 1
    finally:
        playlist.delete()
    assert playlist_name not in [i.title for i in plex.playlists()]


@pytest.mark.client
def test_Play_photos(plex, client, photoalbum):
    photos = photoalbum.photos()
    for photo in photos[:4]:
        client.playMedia(photo)
        time.sleep(2)


def test_Playlist_copyToUser(plex, show, fresh_plex, shared_username):
    episodes = show.episodes()
    playlist = plex.createPlaylist('shared_from_test_plexapi', items=episodes)
    try:
        playlist.copyToUser(shared_username)
        user = plex.myPlexAccount().user(shared_username)
        user_plex = fresh_plex(plex._baseurl, user.get_token(plex.machineIdentifier))
        assert playlist.title in [p.title for p in user_plex.playlists()]
    finally:
        playlist.delete()


def test_Playlist_createSmart(plex, movies, movie):
    try:
        playlist = plex.createPlaylist(
            title='smart_playlist',
            smart=True,
            limit=2,
            section=movies,
            sort='titleSort:desc',
            **{'year>>': 2007}
        )
        items = playlist.items()
        assert playlist.smart
        assert len(items) == 2
        assert items == sorted(items, key=lambda i: i.titleSort, reverse=True)
        playlist.updateFilters(limit=1, year=movie.year)
        playlist.reload()
        assert len(playlist.items()) == 1
        assert movie in playlist
    finally:
        playlist.delete()


def test_Playlist_smartFilters(plex, tvshows):
    try:
        playlist = plex.createPlaylist(
            title="smart_playlist_filters",
            smart=True,
            section=tvshows,
            limit=5,
            libtype='show',
            sort=["season.index:nullsLast", "episode.index:nullsLast", "show.titleSort"],
            filters={"or": [{"show.title": "game"}, {'show.title': "100"}]}
        )
        filters = playlist.filters()
        filters['libtype'] = tvshows.METADATA_TYPE  # Override libtype to check playlist items
        assert tvshows.search(**filters) == playlist.items()
    finally:
        playlist.delete()


def test_Playlist_section(plex, movies, movie):
    title = 'test_playlist_section'
    try:
        playlist = plex.createPlaylist(title, items=movie)
        with pytest.raises(BadRequest):
            playlist.section()
    finally:
        playlist.delete()

    try:
        playlist = plex.createPlaylist(title, smart=True, section=movies, **{'year>>': 2000})
        assert playlist.section() == movies
        playlist.content = ''
        assert playlist.section() == movies
        playlist.updateFilters(year=1990)
        playlist.reload()
        playlist.content = ''
        with pytest.raises(Unsupported):
            playlist.section()
    finally:
        playlist.delete()


def test_Playlist_exceptions(plex, movies, movie, artist):
    title = 'test_playlist_exceptions'
    try:
        playlist = plex.createPlaylist(title, items=movie)
        with pytest.raises(BadRequest):
            playlist.updateFilters()
        with pytest.raises(BadRequest):
            playlist.addItems(artist)
        with pytest.raises(NotFound):
            playlist.removeItems(artist)
        with pytest.raises(NotFound):
            playlist.moveItem(artist)
        with pytest.raises(NotFound):
            playlist.moveItem(item=movie, after=artist)
    finally:
        playlist.delete()

    with pytest.raises(BadRequest):
        plex.createPlaylist(title, items=[])
    with pytest.raises(BadRequest):
        plex.createPlaylist(title, items=[movie, artist])

    try:
        playlist = plex.createPlaylist(title, smart=True, section=movies.title, **{'year>>': 2000})
        with pytest.raises(BadRequest):
            playlist.addItems(movie)
        with pytest.raises(BadRequest):
            playlist.removeItems(movie)
        with pytest.raises(BadRequest):
            playlist.moveItem(movie)
    finally:
        playlist.delete()


def test_Playlist_m3ufile(plex, tvshows, music, m3ufile):
    title = 'test_playlist_m3ufile'
    try:
        playlist = plex.createPlaylist(title, section=music.title, m3ufilepath=m3ufile)
        assert playlist.title == title
    finally:
        playlist.delete()

    with pytest.raises(BadRequest):
        plex.createPlaylist(title, section=tvshows, m3ufilepath='does_not_exist.m3u')
    with pytest.raises(BadRequest):
        plex.createPlaylist(title, section=music, m3ufilepath='does_not_exist.m3u')


def test_Playlist_PlexWebURL(plex, show):
    title = 'test_playlist_plexweburl'
    episodes = show.episodes()
    playlist = plex.createPlaylist(title, items=episodes[:3])
    try:
        url = playlist.getWebURL()
        assert url.startswith('https://app.plex.tv/desktop')
        assert plex.machineIdentifier in url
        assert 'playlist' in url
        assert quote_plus(playlist.key) in url
    finally:
        playlist.delete()


@pytest.mark.xfail(reason="Changing images fails randomly")
def test_Playlist_mixins_images(playlist):
    test_mixins.lock_art(playlist)
    test_mixins.lock_poster(playlist)
    test_mixins.edit_art(playlist)
    test_mixins.edit_poster(playlist)
