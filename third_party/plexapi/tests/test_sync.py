from plexapi.exceptions import BadRequest
from plexapi.sync import (AUDIO_BITRATE_192_KBPS, PHOTO_QUALITY_MEDIUM,
                          VIDEO_QUALITY_3_MBPS_720p)

from . import conftest as utils


def get_sync_item_from_server(sync_device, sync_item):
    sync_list = sync_device.syncItems()
    for item in sync_list.items:
        if item.id == sync_item.id:
            return item


def is_sync_item_missing(sync_device, sync_item):
    return not get_sync_item_from_server(sync_device, sync_item)


def test_current_device_got_sync_target(clear_sync_device):
    assert "sync-target" in clear_sync_device.provides


def get_media(item, server):
    try:
        return item.getMedia()
    except BadRequest as e:
        if "not_found" in str(e):
            server.refreshSync()
            return None
        else:
            raise


def test_add_movie_to_sync(clear_sync_device, movie):
    new_item = movie.sync(VIDEO_QUALITY_3_MBPS_720p, client=clear_sync_device)
    movie._server.refreshSync()
    item = utils.wait_until(
        get_sync_item_from_server,
        delay=0.5,
        timeout=3,
        sync_device=clear_sync_device,
        sync_item=new_item,
    )
    media_list = utils.wait_until(
        get_media, delay=0.25, timeout=3, item=item, server=movie._server
    )
    assert len(media_list) == 1
    assert media_list[0].ratingKey == movie.ratingKey


def test_delete_sync_item(clear_sync_device, movie):
    new_item = movie.sync(VIDEO_QUALITY_3_MBPS_720p, client=clear_sync_device)
    movie._server.refreshSync()
    new_item_in_myplex = utils.wait_until(
        get_sync_item_from_server,
        delay=0.5,
        timeout=3,
        sync_device=clear_sync_device,
        sync_item=new_item,
    )
    sync_items = clear_sync_device.syncItems()
    for item in sync_items.items:
        item.delete()
    utils.wait_until(
        is_sync_item_missing,
        delay=0.5,
        timeout=3,
        sync_device=clear_sync_device,
        sync_item=new_item_in_myplex,
    )


def test_add_show_to_sync(clear_sync_device, show):
    new_item = show.sync(VIDEO_QUALITY_3_MBPS_720p, client=clear_sync_device)
    show._server.refreshSync()
    item = utils.wait_until(
        get_sync_item_from_server,
        delay=0.5,
        timeout=3,
        sync_device=clear_sync_device,
        sync_item=new_item,
    )
    episodes = show.episodes()
    media_list = utils.wait_until(
        get_media, delay=0.25, timeout=3, item=item, server=show._server
    )
    assert len(episodes) == len(media_list)
    assert [e.ratingKey for e in episodes] == [m.ratingKey for m in media_list]


def test_add_season_to_sync(clear_sync_device, show):
    season = show.season("Season 1")
    new_item = season.sync(VIDEO_QUALITY_3_MBPS_720p, client=clear_sync_device)
    season._server.refreshSync()
    item = utils.wait_until(
        get_sync_item_from_server,
        delay=0.5,
        timeout=3,
        sync_device=clear_sync_device,
        sync_item=new_item,
    )
    episodes = season.episodes()
    media_list = utils.wait_until(
        get_media, delay=0.25, timeout=3, item=item, server=season._server
    )
    assert len(episodes) == len(media_list)
    assert [e.ratingKey for e in episodes] == [m.ratingKey for m in media_list]


def test_add_episode_to_sync(clear_sync_device, episode):
    new_item = episode.sync(VIDEO_QUALITY_3_MBPS_720p, client=clear_sync_device)
    episode._server.refreshSync()
    item = utils.wait_until(
        get_sync_item_from_server,
        delay=0.5,
        timeout=3,
        sync_device=clear_sync_device,
        sync_item=new_item,
    )
    media_list = utils.wait_until(
        get_media, delay=0.25, timeout=3, item=item, server=episode._server
    )
    assert 1 == len(media_list)
    assert episode.ratingKey == media_list[0].ratingKey


def test_limited_watched(clear_sync_device, show):
    show.markUnplayed()
    new_item = show.sync(
        VIDEO_QUALITY_3_MBPS_720p, client=clear_sync_device, limit=5, unwatched=False
    )
    show._server.refreshSync()
    item = utils.wait_until(
        get_sync_item_from_server,
        delay=0.5,
        timeout=3,
        sync_device=clear_sync_device,
        sync_item=new_item,
    )
    episodes = show.episodes()[:5]
    media_list = utils.wait_until(
        get_media, delay=0.25, timeout=3, item=item, server=show._server
    )
    assert 5 == len(media_list)
    assert [e.ratingKey for e in episodes] == [m.ratingKey for m in media_list]
    episodes[0].markPlayed()
    show._server.refreshSync()
    media_list = utils.wait_until(
        get_media, delay=0.25, timeout=3, item=item, server=show._server
    )
    assert 5 == len(media_list)
    assert [e.ratingKey for e in episodes] == [m.ratingKey for m in media_list]


def test_limited_unwatched(clear_sync_device, show):
    show.markUnplayed()
    new_item = show.sync(
        VIDEO_QUALITY_3_MBPS_720p, client=clear_sync_device, limit=5, unwatched=True
    )
    show._server.refreshSync()
    item = utils.wait_until(
        get_sync_item_from_server,
        delay=0.5,
        timeout=3,
        sync_device=clear_sync_device,
        sync_item=new_item,
    )
    episodes = show.episodes(viewCount=0)[:5]
    media_list = utils.wait_until(
        get_media, delay=0.25, timeout=3, item=item, server=show._server
    )
    assert len(episodes) == len(media_list)
    assert [e.ratingKey for e in episodes] == [m.ratingKey for m in media_list]
    episodes[0].markPlayed()
    show._server.refreshSync()
    episodes = show.episodes(viewCount=0)[:5]
    media_list = utils.wait_until(
        get_media, delay=0.25, timeout=3, item=item, server=show._server
    )
    assert len(episodes) == len(media_list)
    assert [e.ratingKey for e in episodes] == [m.ratingKey for m in media_list]


def test_unlimited_and_watched(clear_sync_device, show):
    show.markUnplayed()
    new_item = show.sync(
        VIDEO_QUALITY_3_MBPS_720p, client=clear_sync_device, unwatched=False
    )
    show._server.refreshSync()
    item = utils.wait_until(
        get_sync_item_from_server,
        delay=0.5,
        timeout=3,
        sync_device=clear_sync_device,
        sync_item=new_item,
    )
    episodes = show.episodes()
    media_list = utils.wait_until(
        get_media, delay=0.25, timeout=3, item=item, server=show._server
    )
    assert len(episodes) == len(media_list)
    assert [e.ratingKey for e in episodes] == [m.ratingKey for m in media_list]
    episodes[0].markPlayed()
    show._server.refreshSync()
    episodes = show.episodes()
    media_list = utils.wait_until(
        get_media, delay=0.25, timeout=3, item=item, server=show._server
    )
    assert len(episodes) == len(media_list)
    assert [e.ratingKey for e in episodes] == [m.ratingKey for m in media_list]


def test_unlimited_and_unwatched(clear_sync_device, show):
    show.markUnplayed()
    new_item = show.sync(
        VIDEO_QUALITY_3_MBPS_720p, client=clear_sync_device, unwatched=True
    )
    show._server.refreshSync()
    item = utils.wait_until(
        get_sync_item_from_server,
        delay=0.5,
        timeout=3,
        sync_device=clear_sync_device,
        sync_item=new_item,
    )
    episodes = show.episodes(viewCount=0)
    media_list = utils.wait_until(
        get_media, delay=0.25, timeout=3, item=item, server=show._server
    )
    assert len(episodes) == len(media_list)
    assert [e.ratingKey for e in episodes] == [m.ratingKey for m in media_list]
    episodes[0].markPlayed()
    show._server.refreshSync()
    episodes = show.episodes(viewCount=0)
    media_list = utils.wait_until(
        get_media, delay=0.25, timeout=3, item=item, server=show._server
    )
    assert len(episodes) == len(media_list)
    assert [e.ratingKey for e in episodes] == [m.ratingKey for m in media_list]


def test_add_music_artist_to_sync(clear_sync_device, artist):
    new_item = artist.sync(AUDIO_BITRATE_192_KBPS, client=clear_sync_device)
    artist._server.refreshSync()
    item = utils.wait_until(
        get_sync_item_from_server,
        delay=0.5,
        timeout=3,
        sync_device=clear_sync_device,
        sync_item=new_item,
    )
    tracks = artist.tracks()
    media_list = utils.wait_until(
        get_media, delay=0.25, timeout=3, item=item, server=artist._server
    )
    assert len(tracks) == len(media_list)
    assert [t.ratingKey for t in tracks] == [m.ratingKey for m in media_list]


def test_add_music_album_to_sync(clear_sync_device, album):
    new_item = album.sync(AUDIO_BITRATE_192_KBPS, client=clear_sync_device)
    album._server.refreshSync()
    item = utils.wait_until(
        get_sync_item_from_server,
        delay=0.5,
        timeout=3,
        sync_device=clear_sync_device,
        sync_item=new_item,
    )
    tracks = album.tracks()
    media_list = utils.wait_until(
        get_media, delay=0.25, timeout=3, item=item, server=album._server
    )
    assert len(tracks) == len(media_list)
    assert [t.ratingKey for t in tracks] == [m.ratingKey for m in media_list]


def test_add_music_track_to_sync(clear_sync_device, track):
    new_item = track.sync(AUDIO_BITRATE_192_KBPS, client=clear_sync_device)
    track._server.refreshSync()
    item = utils.wait_until(
        get_sync_item_from_server,
        delay=0.5,
        timeout=3,
        sync_device=clear_sync_device,
        sync_item=new_item,
    )
    media_list = utils.wait_until(
        get_media, delay=0.25, timeout=3, item=item, server=track._server
    )
    assert 1 == len(media_list)
    assert track.ratingKey == media_list[0].ratingKey


def test_add_photo_to_sync(clear_sync_device, photoalbum):
    photo = photoalbum.photo("photo1")
    new_item = photo.sync(PHOTO_QUALITY_MEDIUM, client=clear_sync_device)
    photo._server.refreshSync()
    item = utils.wait_until(
        get_sync_item_from_server,
        delay=0.5,
        timeout=3,
        sync_device=clear_sync_device,
        sync_item=new_item,
    )
    media_list = utils.wait_until(
        get_media, delay=0.25, timeout=3, item=item, server=photo._server
    )
    assert 1 == len(media_list)
    assert photo.ratingKey == media_list[0].ratingKey


def test_sync_entire_library_movies(clear_sync_device, movies):
    new_item = movies.sync(VIDEO_QUALITY_3_MBPS_720p, client=clear_sync_device)
    movies._server.refreshSync()
    item = utils.wait_until(
        get_sync_item_from_server,
        delay=0.5,
        timeout=3,
        sync_device=clear_sync_device,
        sync_item=new_item,
    )
    section_content = movies.all()
    media_list = utils.wait_until(
        get_media, delay=0.25, timeout=3, item=item, server=movies._server
    )
    assert len(section_content) == len(media_list)
    assert [e.ratingKey for e in section_content] == [m.ratingKey for m in media_list]


def test_sync_entire_library_tvshows(clear_sync_device, tvshows):
    new_item = tvshows.sync(VIDEO_QUALITY_3_MBPS_720p, client=clear_sync_device)
    tvshows._server.refreshSync()
    item = utils.wait_until(
        get_sync_item_from_server,
        delay=0.5,
        timeout=3,
        sync_device=clear_sync_device,
        sync_item=new_item,
    )
    section_content = tvshows.searchEpisodes()
    media_list = utils.wait_until(
        get_media, delay=0.25, timeout=3, item=item, server=tvshows._server
    )
    assert len(section_content) == len(media_list)
    assert [e.ratingKey for e in section_content] == [m.ratingKey for m in media_list]


def test_sync_entire_library_music(clear_sync_device, music):
    new_item = music.sync(AUDIO_BITRATE_192_KBPS, client=clear_sync_device)
    music._server.refreshSync()
    item = utils.wait_until(
        get_sync_item_from_server,
        delay=0.5,
        timeout=3,
        sync_device=clear_sync_device,
        sync_item=new_item,
    )
    section_content = music.searchTracks()
    media_list = utils.wait_until(
        get_media, delay=0.25, timeout=3, item=item, server=music._server
    )
    assert len(section_content) == len(media_list)
    assert [e.ratingKey for e in section_content] == [m.ratingKey for m in media_list]


def test_sync_entire_library_photos(clear_sync_device, photos):
    new_item = photos.sync(PHOTO_QUALITY_MEDIUM, client=clear_sync_device)
    photos._server.refreshSync()
    item = utils.wait_until(
        get_sync_item_from_server,
        delay=0.5,
        timeout=3,
        sync_device=clear_sync_device,
        sync_item=new_item,
    )
    # It's not that easy, to just get all the photos within the library, so let's query for photos with device!=0x0
    section_content = photos.search(libtype="photo", **{"addedAt>>": "2000-01-01"})
    media_list = utils.wait_until(
        get_media, delay=0.25, timeout=3, item=item, server=photos._server
    )
    assert len(section_content) == len(media_list)
    assert [e.ratingKey for e in section_content] == [m.ratingKey for m in media_list]


def test_playlist_movie_sync(plex, clear_sync_device, movies):
    items = movies.all()
    playlist = plex.createPlaylist("Sync: Movies", items=items)
    new_item = playlist.sync(
        videoQuality=VIDEO_QUALITY_3_MBPS_720p, client=clear_sync_device
    )
    playlist._server.refreshSync()
    item = utils.wait_until(
        get_sync_item_from_server,
        delay=0.5,
        timeout=3,
        sync_device=clear_sync_device,
        sync_item=new_item,
    )
    media_list = utils.wait_until(
        get_media, delay=0.25, timeout=3, item=item, server=playlist._server
    )
    assert len(items) == len(media_list)
    assert [e.ratingKey for e in items] == [m.ratingKey for m in media_list]
    playlist.delete()


def test_playlist_tvshow_sync(plex, clear_sync_device, show):
    items = show.episodes()
    playlist = plex.createPlaylist("Sync: TV Show", items=items)
    new_item = playlist.sync(
        videoQuality=VIDEO_QUALITY_3_MBPS_720p, client=clear_sync_device
    )
    playlist._server.refreshSync()
    item = utils.wait_until(
        get_sync_item_from_server,
        delay=0.5,
        timeout=3,
        sync_device=clear_sync_device,
        sync_item=new_item,
    )
    media_list = utils.wait_until(
        get_media, delay=0.25, timeout=3, item=item, server=playlist._server
    )
    assert len(items) == len(media_list)
    assert [e.ratingKey for e in items] == [m.ratingKey for m in media_list]
    playlist.delete()


def test_playlist_mixed_sync(plex, clear_sync_device, movie, episode):
    items = [movie, episode]
    playlist = plex.createPlaylist("Sync: Mixed", items=items)
    new_item = playlist.sync(
        videoQuality=VIDEO_QUALITY_3_MBPS_720p, client=clear_sync_device
    )
    playlist._server.refreshSync()
    item = utils.wait_until(
        get_sync_item_from_server,
        delay=0.5,
        timeout=3,
        sync_device=clear_sync_device,
        sync_item=new_item,
    )
    media_list = utils.wait_until(
        get_media, delay=0.25, timeout=3, item=item, server=playlist._server
    )
    assert len(items) == len(media_list)
    assert [e.ratingKey for e in items] == [m.ratingKey for m in media_list]
    playlist.delete()


def test_playlist_music_sync(plex, clear_sync_device, artist):
    items = artist.tracks()
    playlist = plex.createPlaylist("Sync: Music", items=items)
    new_item = playlist.sync(
        audioBitrate=AUDIO_BITRATE_192_KBPS, client=clear_sync_device
    )
    playlist._server.refreshSync()
    item = utils.wait_until(
        get_sync_item_from_server,
        delay=0.5,
        timeout=3,
        sync_device=clear_sync_device,
        sync_item=new_item,
    )
    media_list = utils.wait_until(
        get_media, delay=0.25, timeout=3, item=item, server=playlist._server
    )
    assert len(items) == len(media_list)
    assert [e.ratingKey for e in items] == [m.ratingKey for m in media_list]
    playlist.delete()


def test_playlist_photos_sync(plex, clear_sync_device, photoalbum):
    items = photoalbum.photos()
    playlist = plex.createPlaylist("Sync: Photos", items=items)
    new_item = playlist.sync(
        photoResolution=PHOTO_QUALITY_MEDIUM, client=clear_sync_device
    )
    playlist._server.refreshSync()
    item = utils.wait_until(
        get_sync_item_from_server,
        delay=0.5,
        timeout=3,
        sync_device=clear_sync_device,
        sync_item=new_item,
    )
    media_list = utils.wait_until(
        get_media, delay=0.25, timeout=3, item=item, server=playlist._server
    )
    assert len(items) == len(media_list)
    assert [e.ratingKey for e in items] == [m.ratingKey for m in media_list]
    playlist.delete()


def test_collection_sync(plex, clear_sync_device, movies, movie):
    items = [movie]
    collection = plex.createCollection("Sync: Collection", section=movies, items=items)
    new_item = collection.sync(
        videoQuality=VIDEO_QUALITY_3_MBPS_720p, client=clear_sync_device
    )
    collection._server.refreshSync()
    item = utils.wait_until(
        get_sync_item_from_server,
        delay=0.5,
        timeout=3,
        sync_device=clear_sync_device,
        sync_item=new_item,
    )
    media_list = utils.wait_until(
        get_media, delay=0.25, timeout=3, item=item, server=collection._server
    )
    assert len(items) == len(media_list)
    assert [e.ratingKey for e in items] == [m.ratingKey for m in media_list]
    collection.delete()
