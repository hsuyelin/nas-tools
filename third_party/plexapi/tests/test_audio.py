# -*- coding: utf-8 -*-
from urllib.parse import quote_plus

import pytest
from plexapi.exceptions import BadRequest

from . import conftest as utils
from . import test_media, test_mixins


def test_audio_Artist_attr(artist):
    artist.reload()
    assert utils.is_datetime(artist.addedAt)
    assert artist.albumSort == -1
    if artist.art:
        assert utils.is_art(artist.art)
    if artist.countries:
        assert "United States of America" in [i.tag for i in artist.countries]
    # assert "Electronic" in [i.tag for i in artist.genres]
    assert artist.guid == "plex://artist/5d07bdaf403c64029060f8c4"
    assert "mbid://069a1c1f-14eb-4d36-b0a0-77dffbd67713" in [i.id for i in artist.guids]
    assert artist.index == 1
    assert utils.is_metadata(artist._initpath)
    assert utils.is_metadata(artist.key)
    assert utils.is_int(artist.librarySectionID)
    assert artist.listType == "audio"
    assert utils.is_datetime(artist.lastRatedAt)
    assert utils.is_datetime(artist.lastViewedAt)
    assert len(artist.locations) == 1
    assert len(artist.locations[0]) >= 10
    assert artist.ratingKey >= 1
    assert artist._server._baseurl == utils.SERVER_BASEURL
    assert isinstance(artist.similar, list)
    if artist.summary:
        assert "Alias" in artist.summary
    assert artist.theme is None
    if artist.thumb:
        assert utils.is_thumb(artist.thumb)
    assert artist.title == "Broke For Free"
    assert artist.titleSort == "Broke For Free"
    assert artist.type == "artist"
    assert utils.is_datetime(artist.updatedAt)
    assert utils.is_int(artist.viewCount, gte=0)


def test_audio_Artist_get(artist):
    track = artist.get(album="Layers", title="As Colourful as Ever")
    assert track.title == "As Colourful as Ever"


def test_audio_Artist_history(artist):
    history = artist.history()
    assert isinstance(history, list)


def test_audio_Artist_track(artist):
    track = artist.track("As Colourful as Ever")
    assert track.title == "As Colourful as Ever"
    track = artist.track(album="Layers", track=1)
    assert track.parentTitle == "Layers"
    assert track.index == 1
    with pytest.raises(BadRequest):
        artist.track()


def test_audio_Artist_tracks(artist):
    tracks = artist.tracks()
    assert len(tracks) == 1


def test_audio_Artist_album(artist):
    album = artist.album("Layers")
    assert album.title == "Layers"


def test_audio_Artist_albums(artist):
    albums = artist.albums()
    assert len(albums) == 1 and albums[0].title == "Layers"


def test_audio_Artist_hubs(artist):
    hubs = artist.hubs()
    assert isinstance(hubs, list)


def test_audio_Artist_mixins_edit_advanced_settings(artist):
    test_mixins.edit_advanced_settings(artist)


@pytest.mark.xfail(reason="Changing images fails randomly")
def test_audio_Artist_mixins_images(artist):
    test_mixins.lock_art(artist)
    test_mixins.lock_poster(artist)
    test_mixins.edit_art(artist)
    test_mixins.edit_poster(artist)
    test_mixins.attr_artUrl(artist)
    test_mixins.attr_posterUrl(artist)


def test_audio_Artist_mixins_themes(artist):
    test_mixins.edit_theme(artist)


def test_audio_Artist_mixins_rating(artist):
    test_mixins.edit_rating(artist)


def test_audio_Artist_mixins_fields(artist):
    test_mixins.edit_added_at(artist)
    test_mixins.edit_sort_title(artist)
    test_mixins.edit_summary(artist)
    test_mixins.edit_title(artist)


def test_audio_Artist_mixins_tags(artist):
    test_mixins.edit_collection(artist)
    test_mixins.edit_country(artist)
    test_mixins.edit_genre(artist)
    test_mixins.edit_label(artist)
    test_mixins.edit_mood(artist)
    test_mixins.edit_similar_artist(artist)
    test_mixins.edit_style(artist)


def test_audio_Artist_media_tags(artist):
    artist.reload()
    test_media.tag_collection(artist)
    test_media.tag_country(artist)
    test_media.tag_genre(artist)
    test_media.tag_mood(artist)
    test_media.tag_similar(artist)
    test_media.tag_style(artist)


def test_audio_Artist_PlexWebURL(plex, artist):
    url = artist.getWebURL()
    assert url.startswith('https://app.plex.tv/desktop')
    assert plex.machineIdentifier in url
    assert 'details' in url
    assert quote_plus(artist.key) in url


def test_audio_Album_attrs(album):
    assert utils.is_datetime(album.addedAt)
    if album.art:
        assert utils.is_art(album.art)
    assert isinstance(album.formats, list)
    assert isinstance(album.genres, list)
    assert album.guid == "plex://album/5d07c7e5403c640290bb5bfc"
    assert "mbid://80b4a679-a2a4-4d18-835d-3e081185d7ba" in [i.id for i in album.guids]
    assert album.index == 1
    assert utils.is_metadata(album._initpath)
    assert utils.is_metadata(album.key)
    assert utils.is_datetime(album.lastRatedAt)
    assert utils.is_datetime(album.lastViewedAt)
    assert utils.is_int(album.librarySectionID)
    assert album.listType == "audio"
    assert utils.is_datetime(album.originallyAvailableAt)
    assert utils.is_metadata(album.parentKey)
    assert utils.is_int(album.parentRatingKey)
    assert album.parentTheme is None or utils.is_metadata(album.parentTheme)
    if album.parentThumb:
        assert utils.is_thumb(album.parentThumb)
    assert album.parentTitle == "Broke For Free"
    assert album.ratingKey >= 1
    assert album._server._baseurl == utils.SERVER_BASEURL
    assert album.studio == "[no label]"
    assert isinstance(album.subformats, list)
    assert album.summary == ""
    if album.thumb:
        assert utils.is_thumb(album.thumb)
    assert album.title == "Layers"
    assert album.titleSort == "Layers"
    assert album.type == "album"
    assert utils.is_datetime(album.updatedAt)
    assert utils.is_int(album.viewCount, gte=0)
    assert album.year in (2012,)


def test_audio_Album_history(album):
    history = album.history()
    assert isinstance(history, list)


def test_audio_Track_history(track):
    history = track.history()
    assert isinstance(history, list)


def test_audio_Album_tracks(album):
    tracks = album.tracks()
    assert len(tracks) == 1


def test_audio_Album_track(album):
    track = album.track("As Colourful as Ever")
    assert track.title == "As Colourful as Ever"
    track = album.track(track=1)
    assert track.index == 1
    track = album.track(1)
    assert track.index == 1
    with pytest.raises(BadRequest):
        album.track()


def test_audio_Album_get(album):
    track = album.get("As Colourful as Ever")
    assert track.title == "As Colourful as Ever"


def test_audio_Album_artist(album):
    artist = album.artist()
    artist.title == "Broke For Free"


@pytest.mark.xfail(reason="Changing images fails randomly")
def test_audio_Album_mixins_images(album):
    test_mixins.lock_art(album)
    test_mixins.lock_poster(album)
    test_mixins.edit_art(album)
    test_mixins.edit_poster(album)
    test_mixins.attr_artUrl(album)
    test_mixins.attr_posterUrl(album)


def test_audio_Album_mixins_themes(album):
    test_mixins.attr_themeUrl(album)


def test_audio_Album_mixins_rating(album):
    test_mixins.edit_rating(album)


def test_audio_Album_mixins_fields(album):
    test_mixins.edit_added_at(album)
    test_mixins.edit_originally_available(album)
    test_mixins.edit_sort_title(album)
    test_mixins.edit_studio(album)
    test_mixins.edit_summary(album)
    test_mixins.edit_title(album)


def test_audio_Album_mixins_tags(album):
    test_mixins.edit_collection(album)
    test_mixins.edit_genre(album)
    test_mixins.edit_label(album)
    test_mixins.edit_mood(album)
    test_mixins.edit_style(album)


def test_audio_Album_media_tags(album):
    album.reload()
    test_media.tag_collection(album)
    test_media.tag_genre(album)
    test_media.tag_label(album)
    test_media.tag_mood(album)
    test_media.tag_style(album)


def test_audio_Album_PlexWebURL(plex, album):
    url = album.getWebURL()
    assert url.startswith('https://app.plex.tv/desktop')
    assert plex.machineIdentifier in url
    assert 'details' in url
    assert quote_plus(album.key) in url


def test_audio_Track_attrs(album):
    track = album.get("As Colourful As Ever").reload()
    assert utils.is_datetime(track.addedAt)
    if track.art:
        assert utils.is_art(track.art)
    assert track.chapterSource is None
    assert utils.is_int(track.duration)
    if track.grandparentArt:
        assert utils.is_art(track.grandparentArt)
    assert utils.is_metadata(track.grandparentKey)
    assert utils.is_int(track.grandparentRatingKey)
    assert track.grandparentTheme is None or utils.is_metadata(track.grandparentTheme)
    if track.grandparentThumb:
        assert utils.is_thumb(track.grandparentThumb)
    assert track.grandparentTitle == "Broke For Free"
    assert track.guid == "plex://track/5d07e453403c6402907b80aa"
    assert "mbid://6524bc2d-3f58-4afa-9e06-00a651f5d813" in [i.id for i in track.guids]
    assert track.hasSonicAnalysis is False
    assert track.index == 1
    assert track.trackNumber == track.index
    assert utils.is_metadata(track._initpath)
    assert utils.is_metadata(track.key)
    assert utils.is_datetime(track.lastRatedAt)
    assert utils.is_datetime(track.lastViewedAt)
    assert utils.is_int(track.librarySectionID)
    assert track.listType == "audio"
    assert len(track.locations) == 1
    assert len(track.locations[0]) >= 10
    # Assign 0 track.media
    media = track.media[0]
    assert track.moods == []
    assert track.originalTitle in (None, "Broke For Free")
    assert int(track.parentIndex) == 1
    assert utils.is_metadata(track.parentKey)
    assert utils.is_int(track.parentRatingKey)
    if track.parentThumb:
        assert utils.is_thumb(track.parentThumb)
    assert track.parentTitle == "Layers"
    assert track.playlistItemID is None
    assert track.primaryExtraKey is None
    assert track.ratingCount is None or utils.is_int(track.ratingCount)
    assert utils.is_int(track.ratingKey)
    assert track._server._baseurl == utils.SERVER_BASEURL
    assert track.skipCount is None
    assert track.summary == ""
    if track.thumb:
        assert utils.is_thumb(track.thumb)
    assert track.title == "As Colourful as Ever"
    assert track.titleSort == "As Colourful as Ever"
    assert track.type == "track"
    assert utils.is_datetime(track.updatedAt)
    assert utils.is_int(track.viewCount, gte=0)
    assert track.viewOffset == 0
    assert track.viewedAt is None
    assert track.year is None
    assert track.url(None) is None
    assert media.aspectRatio is None
    assert media.audioChannels == 2
    assert media.audioCodec == "mp3"
    assert media.bitrate == 128
    assert media.container == "mp3"
    assert utils.is_int(media.duration)
    assert media.height is None
    assert utils.is_int(media.id, gte=1)
    assert utils.is_metadata(media._initpath)
    assert media.optimizedForStreaming is None
    # Assign 0 media.parts
    part = media.parts[0]
    assert media._server._baseurl == utils.SERVER_BASEURL
    assert media.videoCodec is None
    assert media.videoFrameRate is None
    assert media.videoResolution is None
    assert media.width is None
    assert part.container == "mp3"
    assert utils.is_int(part.duration)
    assert part.file.endswith(".mp3")
    assert utils.is_int(part.id)
    assert utils.is_metadata(part._initpath)
    assert utils.is_part(part.key)
    # assert part.media == <Media:Holy.Moment>
    assert part._server._baseurl == utils.SERVER_BASEURL
    assert part.size == 3761053
    # Assign 0 part.streams
    stream = part.streams[0]
    assert stream.audioChannelLayout == "stereo"
    assert stream.bitDepth is None
    assert stream.bitrate == 128
    assert stream.bitrateMode is None
    assert stream.channels == 2
    assert stream.codec == "mp3"
    assert stream.duration is None
    assert utils.is_int(stream.id)
    assert stream.index == 0
    assert utils.is_metadata(stream._initpath)
    assert stream.language is None
    assert stream.languageCode is None
    # assert stream.part == <MediaPart:22>
    assert stream.samplingRate == 48000
    assert stream.selected is True
    assert stream._server._baseurl == utils.SERVER_BASEURL
    assert stream.streamType == 2
    assert stream.title is None
    assert stream.type == 2
    assert stream.albumGain is None
    assert stream.albumPeak is None
    assert stream.albumRange is None
    assert stream.endRamp is None
    assert stream.gain is None
    assert stream.loudness is None
    assert stream.lra is None
    assert stream.peak is None
    assert stream.startRamp is None


def test_audio_Track_album(album):
    tracks = album.tracks()
    assert tracks[0].album() == album


def test_audio_Track_artist(album, artist):
    tracks = album.tracks()
    assert tracks[0].artist() == artist


def test_audio_Track_mixins_images(track):
    test_mixins.attr_artUrl(track)
    test_mixins.attr_posterUrl(track)


def test_audio_Track_mixins_themes(track):
    test_mixins.attr_themeUrl(track)


def test_audio_Track_mixins_rating(track):
    test_mixins.edit_rating(track)


def test_audio_Track_mixins_fields(track):
    test_mixins.edit_added_at(track)
    test_mixins.edit_title(track)
    test_mixins.edit_track_artist(track)
    test_mixins.edit_track_number(track)
    test_mixins.edit_track_disc_number(track)


def test_audio_Track_mixins_tags(track):
    test_mixins.edit_collection(track)
    test_mixins.edit_label(track)
    test_mixins.edit_mood(track)


def test_audio_Track_media_tags(track):
    track.reload()
    test_media.tag_collection(track)
    test_media.tag_mood(track)


def test_audio_Track_PlexWebURL(plex, track):
    url = track.getWebURL()
    assert url.startswith('https://app.plex.tv/desktop')
    assert plex.machineIdentifier in url
    assert 'details' in url
    assert quote_plus(track.parentKey) in url


def test_audio_Audio_section(artist, album, track):
    assert artist.section()
    assert album.section()
    assert track.section()
    assert track.section().key == album.section().key == artist.section().key


def test_audio_Artist_download(monkeydownload, tmpdir, artist):
    total = len(artist.tracks())
    filepaths = artist.download(savepath=str(tmpdir))
    assert len(filepaths) == total
    subfolders = artist.download(savepath=str(tmpdir), subfolders=True)
    assert len(subfolders) == total


def test_audio_Album_download(monkeydownload, tmpdir, album):
    total = len(album.tracks())
    filepaths = album.download(savepath=str(tmpdir))
    assert len(filepaths) == total


def test_audio_Track_download(monkeydownload, tmpdir, track):
    filepaths = track.download(savepath=str(tmpdir))
    assert len(filepaths) == 1
