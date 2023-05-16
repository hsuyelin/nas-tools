# -*- coding: utf-8 -*-
import os
from datetime import datetime
from time import sleep
from urllib.parse import quote_plus

import pytest
from plexapi.exceptions import BadRequest, NotFound
from plexapi.sync import VIDEO_QUALITY_3_MBPS_720p

from . import conftest as utils
from . import test_media, test_mixins


def test_video_Movie(movies, movie):
    movie2 = movies.get(movie.title)
    assert movie2.title == movie.title


def test_video_Movie_attributeerror(movie):
    with pytest.raises(AttributeError):
        movie.asshat


def test_video_ne(movies):
    assert (
        len(
            movies.fetchItems(
                f"/library/sections/{movies.key}/all", title__ne="Sintel"
            )
        )
        == 3
    )


def test_video_Movie_delete(movie, patched_http_call):
    movie.delete()


def test_video_Movie_merge(movie, patched_http_call):
    movie.merge(1337)


def test_video_Movie_attrs(movies):
    movie = movies.get("Sita Sings the Blues")
    assert len(movie.locations) == 1
    assert len(movie.locations[0]) >= 10
    assert utils.is_datetime(movie.addedAt)
    if movie.art:
        assert utils.is_art(movie.art)
    assert utils.is_float(movie.rating)
    assert movie.ratingImage == 'rottentomatoes://image.rating.ripe'
    assert utils.is_float(movie.audienceRating)
    assert movie.audienceRatingImage == 'rottentomatoes://image.rating.upright'
    if movie.ratings:
        assert "imdb://image.rating" in [i.image for i in movie.ratings]
    movie.reload()  # RELOAD
    assert movie.chapterSource is None
    assert not movie.collections
    assert movie.contentRating in utils.CONTENTRATINGS
    assert movie.editionTitle is None
    assert movie.enableCreditsMarkerGeneration == -1
    if movie.countries:
        assert "United States of America" in [i.tag for i in movie.countries]
    if movie.producers:
        assert "Nina Paley" in [i.tag for i in movie.producers]
    if movie.directors:
        assert "Nina Paley" in [i.tag for i in movie.directors]
    if movie.roles:
        assert "Reena Shah" in [i.tag for i in movie.roles]
        assert movie.actors == movie.roles
    if movie.writers:
        assert "Nina Paley" in [i.tag for i in movie.writers]
    assert movie.duration >= 160000
    assert not movie.fields
    assert movie.posters()
    assert "Animation" in [i.tag for i in movie.genres]
    assert "imdb://tt1172203" in [i.id for i in movie.guids]
    assert movie.guid == "plex://movie/5d776846880197001ec967c6"
    assert movie.hasPreviewThumbnails is False
    assert utils.is_metadata(movie._initpath)
    assert utils.is_metadata(movie.key)
    assert movie.languageOverride is None
    assert utils.is_datetime(movie.lastRatedAt)
    assert utils.is_datetime(movie.lastViewedAt)
    assert int(movie.librarySectionID) >= 1
    assert movie.listType == "video"
    assert movie.originalTitle is None
    assert utils.is_datetime(movie.originallyAvailableAt)
    assert movie.playlistItemID is None
    if movie.primaryExtraKey:
        assert utils.is_metadata(movie.primaryExtraKey)
    assert movie.ratingKey >= 1
    assert movie._server._baseurl == utils.SERVER_BASEURL
    assert movie.studio == "Nina Paley"
    assert utils.is_string(movie.summary, gte=100)
    assert movie.tagline == "The Greatest Break-Up Story Ever Told."
    assert movie.theme is None
    if movie.thumb:
        assert utils.is_thumb(movie.thumb)
    assert movie.title == "Sita Sings the Blues"
    assert movie.titleSort == "Sita Sings the Blues"
    assert movie.type == "movie"
    assert movie.updatedAt > datetime(2017, 1, 1)
    assert movie.useOriginalTitle == -1
    assert movie.userRating is None
    assert movie.viewCount == 0
    assert utils.is_int(movie.viewOffset, gte=0)
    assert movie.viewedAt is None
    assert movie.year == 2009
    # Audio
    audio = movie.media[0].parts[0].audioStreams()[0]
    if audio.audioChannelLayout:
        assert audio.audioChannelLayout in utils.AUDIOLAYOUTS
    assert audio.bitDepth is None
    assert utils.is_int(audio.bitrate)
    assert audio.bitrateMode is None
    assert audio.channels in utils.AUDIOCHANNELS
    assert audio.codec in utils.CODECS
    assert audio.default is True
    assert audio.displayTitle == "Unknown (AAC Stereo)"
    assert audio.duration is None
    assert audio.extendedDisplayTitle == "Unknown (AAC Stereo)"
    assert audio.id >= 1
    assert audio.index == 1
    assert utils.is_metadata(audio._initpath)
    assert audio.language is None
    assert audio.languageCode is None
    assert audio.languageTag is None
    assert audio.profile == "lc"
    assert audio.requiredBandwidths is None or audio.requiredBandwidths
    assert audio.samplingRate == 44100
    assert audio.selected is True
    assert audio.streamIdentifier == 2
    assert audio.streamType == 2
    assert audio._server._baseurl == utils.SERVER_BASEURL
    assert audio.title is None
    assert audio.type == 2
    with pytest.raises(AttributeError):
        assert audio.albumGain is None  # Check track only attributes are not available
    # Media
    media = movie.media[0]
    assert media.aspectRatio >= 1.3
    assert media.audioChannels in utils.AUDIOCHANNELS
    assert media.audioCodec in utils.CODECS
    assert media.audioProfile == "lc"
    assert utils.is_int(media.bitrate)
    assert media.container in utils.CONTAINERS
    assert utils.is_int(media.duration, gte=160000)
    assert utils.is_int(media.height)
    assert utils.is_int(media.id)
    assert utils.is_metadata(media._initpath)
    assert media.has64bitOffsets is False
    assert media.optimizedForStreaming in [None, False, True]
    assert media.proxyType is None
    assert media._server._baseurl == utils.SERVER_BASEURL
    assert media.target is None
    assert media.title is None
    assert media.videoCodec in utils.CODECS
    assert media.videoFrameRate in utils.FRAMERATES
    assert media.videoProfile == "main"
    assert media.videoResolution in utils.RESOLUTIONS
    assert utils.is_int(media.width, gte=200)
    with pytest.raises(AttributeError):
        assert media.aperture is None  # Check photo only attributes are not available
    # Video
    video = movie.media[0].parts[0].videoStreams()[0]
    assert video.anamorphic is None
    assert video.bitDepth in (
        8,
        None,
    )  # Different versions of Plex Server return different values
    assert utils.is_int(video.bitrate)
    assert video.cabac is None
    assert video.chromaLocation == "left"
    assert video.chromaSubsampling in ("4:2:0", None)
    assert video.codec in utils.CODECS
    assert video.codecID is None
    assert utils.is_int(video.codedHeight, gte=1080)
    assert utils.is_int(video.codedWidth, gte=1920)
    assert video.colorPrimaries is None
    assert video.colorRange is None
    assert video.colorSpace is None
    assert video.colorTrc is None
    assert video.default is True
    assert video.displayTitle == "1080p (H.264)"
    assert video.DOVIBLCompatID is None
    assert video.DOVIBLPresent is None
    assert video.DOVIELPresent is None
    assert video.DOVILevel is None
    assert video.DOVIPresent is None
    assert video.DOVIProfile is None
    assert video.DOVIRPUPresent is None
    assert video.DOVIVersion is None
    assert video.duration is None
    assert video.extendedDisplayTitle == "1080p (H.264)"
    assert utils.is_float(video.frameRate, gte=20.0)
    assert video.frameRateMode is None
    assert video.hasScalingMatrix is False
    assert utils.is_int(video.height, gte=250)
    assert utils.is_int(video.id)
    assert utils.is_int(video.index, gte=0)
    assert utils.is_metadata(video._initpath)
    assert video.language is None
    assert video.languageCode is None
    assert video.languageTag is None
    assert utils.is_int(video.level)
    assert video.profile in utils.PROFILES
    assert video.pixelAspectRatio is None
    assert video.pixelFormat is None
    assert utils.is_int(video.refFrames)
    assert video.requiredBandwidths is None or video.requiredBandwidths
    assert video.scanType in ("progressive", None)
    assert video.selected is False
    assert video.streamType == 1
    assert video.streamIdentifier == 1
    assert video._server._baseurl == utils.SERVER_BASEURL
    assert utils.is_int(video.streamType)
    assert video.title is None
    assert video.type == 1
    assert utils.is_int(video.width, gte=400)
    # Part
    part = media.parts[0]
    assert part.accessible
    assert part.audioProfile == "lc"
    assert part.container in utils.CONTAINERS
    assert part.decision is None
    assert part.deepAnalysisVersion is None or utils.is_int(part.deepAnalysisVersion)
    assert utils.is_int(part.duration, gte=160000)
    assert part.exists
    assert len(part.file) >= 10
    assert part.has64bitOffsets is False
    assert part.hasPreviewThumbnails is False
    assert part.hasThumbnail is None
    assert utils.is_int(part.id)
    assert part.indexes is None
    assert utils.is_metadata(part._initpath)
    assert len(part.key) >= 10
    assert part.optimizedForStreaming is True
    assert part.packetLength is None
    assert part.requiredBandwidths is None or part.requiredBandwidths
    assert utils.is_int(part.size, gte=1000000)
    assert part.syncItemId is None
    assert part.syncState is None
    assert part._server._baseurl == utils.SERVER_BASEURL
    assert part.videoProfile == "main"
    # Stream 1
    stream1 = part.streams[0]
    assert stream1.bitDepth in (8, None)
    assert utils.is_int(stream1.bitrate)
    assert stream1.cabac is None
    assert stream1.chromaSubsampling in ("4:2:0", None)
    assert stream1.codec in utils.CODECS
    assert stream1.colorSpace is None
    assert stream1.duration is None
    assert utils.is_float(stream1.frameRate, gte=20.0)
    assert stream1.frameRateMode is None
    assert stream1.hasScalingMatrix is False
    assert utils.is_int(stream1.height, gte=250)
    assert utils.is_int(stream1.id)
    assert utils.is_int(stream1.index, gte=0)
    assert utils.is_metadata(stream1._initpath)
    assert stream1.language is None
    assert stream1.languageCode is None
    assert stream1.languageTag is None
    assert utils.is_int(stream1.level)
    assert stream1.profile in utils.PROFILES
    assert utils.is_int(stream1.refFrames)
    assert stream1.scanType in ("progressive", None)
    assert stream1.selected is False
    assert stream1._server._baseurl == utils.SERVER_BASEURL
    assert utils.is_int(stream1.streamType)
    assert stream1.title is None
    assert stream1.type == 1
    assert utils.is_int(stream1.width, gte=400)
    # Stream 2
    stream2 = part.streams[1]
    if stream2.audioChannelLayout:
        assert stream2.audioChannelLayout in utils.AUDIOLAYOUTS
    assert stream2.bitDepth is None
    assert utils.is_int(stream2.bitrate)
    assert stream2.bitrateMode is None
    assert stream2.channels in utils.AUDIOCHANNELS
    assert stream2.codec in utils.CODECS
    assert stream2.duration is None
    assert utils.is_int(stream2.id)
    assert utils.is_int(stream2.index)
    assert utils.is_metadata(stream2._initpath)
    assert stream2.language is None
    assert stream2.languageCode is None
    assert stream2.languageTag is None
    assert utils.is_int(stream2.samplingRate)
    assert stream2.selected is True
    assert stream2._server._baseurl == utils.SERVER_BASEURL
    assert stream2.streamType == 2
    assert stream2.title is None
    assert stream2.type == 2


def test_video_Movie_media_tags_Exception(movie):
    with pytest.raises(BadRequest):
        movie.genres[0].items()


def test_video_Movie_media_tags_collection(movie, collection):
    movie.reload()
    collection_tag = next(c for c in movie.collections if c.tag == "Test Collection")
    assert collection == collection_tag.collection()


def test_video_Movie_getStreamURL(movie, account):
    key = movie.key

    url = movie.getStreamURL()
    assert url.startswith(f"{utils.SERVER_BASEURL}/video/:/transcode/universal/start.m3u8")
    assert account.authenticationToken in url
    assert f"path={quote_plus(key)}" in url
    assert "protocol" not in url
    assert "videoResolution" not in url

    url = movie.getStreamURL(videoResolution="800x600", protocol='dash')
    assert url.startswith(f"{utils.SERVER_BASEURL}/video/:/transcode/universal/start.mpd")
    assert "protocol=dash" in url
    assert "videoResolution=800x600" in url


def test_video_Movie_isFullObject_and_reload(plex):
    movie = plex.library.section("Movies").get("Sita Sings the Blues")
    assert movie.isFullObject() is False
    movie.reload(checkFiles=False)
    assert movie.isFullObject() is False
    movie.reload()
    assert movie.isFullObject() is True
    movie_via_search = plex.library.search(movie.title)[0]
    assert movie_via_search.isFullObject() is False
    movie_via_search.reload()
    assert movie_via_search.isFullObject() is True
    movie_via_section_search = plex.library.section("Movies").search(movie.title)[0]
    assert movie_via_section_search.isFullObject() is False
    movie_via_section_search.reload()
    assert movie_via_section_search.isFullObject() is True
    # If the verify that the object has been reloaded. xml from search only returns 3 actors.
    assert len(movie_via_section_search.roles) >= 3


def test_video_movie_watched(movie):
    movie.markUnplayed()
    movie.markPlayed()
    movie.reload()
    assert movie.viewCount == 1
    movie.markUnplayed()
    movie.reload()
    assert movie.viewCount == 0


def test_video_Movie_isPartialObject(movie):
    assert movie.isPartialObject()
    movie._autoReload = False
    assert movie.originalTitle is None
    assert movie.isPartialObject()
    movie._autoReload = True


def test_video_Movie_media_delete(movie, patched_http_call):
    for media in movie.media:
        media.delete()


def test_video_Movie_iterParts(movie):
    assert len(list(movie.iterParts())) >= 1


def test_video_Movie_download(monkeydownload, tmpdir, movie):
    filepaths = movie.download(savepath=str(tmpdir))
    assert len(filepaths) == 1
    with_resolution = movie.download(
        savepath=str(tmpdir), keep_original_filename=True, videoResolution="500x300"
    )
    assert len(with_resolution) == 1
    filename = os.path.basename(movie.media[0].parts[0].file)
    assert filename in with_resolution[0]


def test_video_Movie_videoStreams(movie):
    assert movie.videoStreams()

    
def test_video_Movie_audioStreams(movie):
    assert movie.audioStreams()


def test_video_Movie_subtitleStreams(movie):
    assert not movie.subtitleStreams()


def test_video_Episode_subtitleStreams(episode):
    assert not episode.subtitleStreams()


def test_video_Movie_upload_select_remove_subtitle(movie, subtitle):

    filepath = os.path.realpath(subtitle.name)

    movie.uploadSubtitles(filepath)
    subtitles = [sub.title for sub in movie.subtitleStreams()]
    subname = subtitle.name.rsplit(".", 1)[0]
    assert subname in subtitles

    movie.subtitleStreams()[0].setDefault()
    movie.reload()

    subtitleSelection = movie.subtitleStreams()[0]
    assert subtitleSelection.selected

    movie.removeSubtitles(streamTitle=subname)
    movie.reload()
    subtitles = [sub.title for sub in movie.subtitleStreams()]
    assert subname not in subtitles

    try:
        os.remove(filepath)
    except:
        pass


def test_video_Movie_match(movies):
    sectionAgent = movies.agent
    sectionAgents = [agent.identifier for agent in movies.agents() if agent.shortIdentifier != 'none']
    sectionAgents.remove(sectionAgent)
    altAgent = sectionAgents[0]

    movie = movies.all()[0]
    title = movie.title
    year = str(movie.year)
    titleUrlEncode = quote_plus(title)

    def parse_params(key):
        params = key.split('?', 1)[1]
        params = params.split("&")
        return {x.split("=")[0]: x.split("=")[1] for x in params}

    results = movie.matches(title="", year="")
    if results:
        initpath = results[0]._initpath
        assert initpath.startswith(movie.key)
        params = initpath.split(movie.key)[1]
        parsedParams = parse_params(params)
        assert parsedParams.get('manual') == '1'
        assert parsedParams.get('title') == ""
        assert parsedParams.get('year') == ""
        assert parsedParams.get('agent') == sectionAgent
    else:
        assert len(results) == 0

    results = movie.matches(title=title, year="", agent=sectionAgent)
    if results:
        initpath = results[0]._initpath
        assert initpath.startswith(movie.key)
        params = initpath.split(movie.key)[1]
        parsedParams = parse_params(params)
        assert parsedParams.get('manual') == '1'
        assert parsedParams.get('title') == titleUrlEncode
        assert parsedParams.get('year') == ""
        assert parsedParams.get('agent') == sectionAgent
    else:
        assert len(results) == 0

    results = movie.matches(title=title, agent=sectionAgent)
    if results:
        initpath = results[0]._initpath
        assert initpath.startswith(movie.key)
        params = initpath.split(movie.key)[1]
        parsedParams = parse_params(params)
        assert parsedParams.get('manual') == '1'
        assert parsedParams.get('title') == titleUrlEncode
        assert parsedParams.get('year') == year
        assert parsedParams.get('agent') == sectionAgent
    else:
        assert len(results) == 0

    results = movie.matches(title="", year="")
    if results:
        initpath = results[0]._initpath
        assert initpath.startswith(movie.key)
        params = initpath.split(movie.key)[1]
        parsedParams = parse_params(params)
        assert parsedParams.get('manual') == '1'
        assert parsedParams.get('agent') == sectionAgent
    else:
        assert len(results) == 0

    results = movie.matches(title="", year="", agent=altAgent)
    if results:
        initpath = results[0]._initpath
        assert initpath.startswith(movie.key)
        params = initpath.split(movie.key)[1]
        parsedParams = parse_params(params)
        assert parsedParams.get('manual') == '1'
        assert parsedParams.get('agent') == altAgent
    else:
        assert len(results) == 0

    results = movie.matches(agent=altAgent)
    if results:
        initpath = results[0]._initpath
        assert initpath.startswith(movie.key)
        params = initpath.split(movie.key)[1]
        parsedParams = parse_params(params)
        assert parsedParams.get('manual') == '1'
        assert parsedParams.get('agent') == altAgent
    else:
        assert len(results) == 0

    results = movie.matches()
    if results:
        initpath = results[0]._initpath
        assert initpath.startswith(movie.key)
        params = initpath.split(movie.key)[1]
        parsedParams = parse_params(params)
        assert parsedParams.get('manual') == '1'
    else:
        assert len(results) == 0


def test_video_Movie_hubs(movies):
    movie = movies.get('Big Buck Bunny')
    hubs = movie.hubs()
    assert len(hubs)
    hub = hubs[0]
    assert hub.context == "hub.movie.similar"
    assert utils.is_metadata(hub.hubKey)
    assert hub.hubIdentifier == "movie.similar"
    assert len(hub.items) == hub.size
    assert utils.is_metadata(hub.key)
    assert hub.more is False
    assert hub.size == 1
    assert hub.style in (None, "shelf")
    assert hub.title == "Related Movies"
    assert hub.type == "movie"
    assert len(hub) == hub.size
    # Force hub reload
    hub.more = True
    hub.reload()
    assert len(hub.items) == hub.size
    assert hub.more is False
    assert hub.size == 1


@pytest.mark.authenticated
@pytest.mark.xfail(reason="Test account is missing online media sources?")
def test_video_Movie_augmentation(movie, account):
    onlineMediaSources = account.onlineMediaSources()
    tidalOptOut = next(
        optOut for optOut in onlineMediaSources
        if optOut.key == 'tv.plex.provider.music'
    )
    optOutValue = tidalOptOut.value

    tidalOptOut.optOut()
    with pytest.raises(BadRequest):
        movie.augmentation()

    tidalOptOut.optIn()
    augmentations = movie.augmentation()
    assert augmentations or augmentations == []

    # Reset original Tidal opt out value
    tidalOptOut._updateOptOut(optOutValue)


def test_video_Movie_reviews(movies):
    movie = movies.get("Sita Sings The Blues")
    reviews = movie.reviews()
    assert reviews
    review = next(r for r in reviews if r.link)
    assert review.filter
    assert utils.is_int(review.id)
    assert review.image.startswith("rottentomatoes://")
    assert review.link.startswith("http")
    assert review.source
    assert review.tag
    assert review.text


def test_video_Movie_editions(movie):
    assert len(movie.editions()) == 0


@pytest.mark.authenticated
def test_video_Movie_extras(movies):
    movie = movies.get("Sita Sings The Blues")
    extras = movie.extras()
    assert extras
    extra = extras[0]
    assert extra.type == 'clip'
    assert extra.section() == movies


def test_video_Movie_batchEdits(movie):
    title = movie.title
    summary = movie.summary
    tagline = movie.tagline
    studio = movie.studio

    assert movie._edits is None
    movie.batchEdits()
    assert movie._edits == {}

    new_title = "New title"
    new_summary = "New summary"
    new_tagline = "New tagline"
    new_studio = "New studio"
    movie.editTitle(new_title) \
        .editSummary(new_summary) \
        .editTagline(new_tagline) \
        .editStudio(new_studio)
    assert movie._edits != {}
    movie.saveEdits()
    assert movie._edits is None
    assert movie.title == new_title
    assert movie.summary == new_summary
    assert movie.tagline == new_tagline
    assert movie.studio == new_studio

    movie.batchEdits() \
        .editTitle(title, locked=False) \
        .editSummary(summary, locked=False) \
        .editTagline(tagline, locked=False) \
        .editStudio(studio, locked=False) \
        .saveEdits()
    assert movie.title == title
    assert movie.summary == summary
    assert movie.tagline == tagline
    assert movie.studio == studio
    assert not movie.fields
    
    with pytest.raises(BadRequest):
        movie.saveEdits()


def test_video_Movie_mixins_edit_advanced_settings(movie):
    test_mixins.edit_advanced_settings(movie)


@pytest.mark.xfail(reason="Changing images fails randomly")
def test_video_Movie_mixins_images(movie):
    test_mixins.lock_art(movie)
    test_mixins.lock_poster(movie)
    test_mixins.edit_art(movie)
    test_mixins.edit_poster(movie)


def test_video_Movie_mixins_themes(movie):
    test_mixins.edit_theme(movie)


def test_video_Movie_mixins_rating(movie):
    test_mixins.edit_rating(movie)


def test_video_Movie_mixins_fields(movie):
    test_mixins.edit_added_at(movie)
    test_mixins.edit_content_rating(movie)
    test_mixins.edit_originally_available(movie)
    test_mixins.edit_original_title(movie)
    test_mixins.edit_sort_title(movie)
    test_mixins.edit_studio(movie)
    test_mixins.edit_summary(movie)
    test_mixins.edit_tagline(movie)
    test_mixins.edit_title(movie)
    with pytest.raises(BadRequest):
        test_mixins.edit_edition_title(movie)


@pytest.mark.authenticated
def test_video_Movie_mixins_fields(movie):
    test_mixins.edit_edition_title(movie)


def test_video_Movie_mixins_tags(movie):
    test_mixins.edit_collection(movie)
    test_mixins.edit_country(movie)
    test_mixins.edit_director(movie)
    test_mixins.edit_genre(movie)
    test_mixins.edit_label(movie)
    test_mixins.edit_producer(movie)
    test_mixins.edit_writer(movie)


def test_video_Movie_media_tags(movie):
    movie.reload()
    test_media.tag_collection(movie)
    test_media.tag_country(movie)
    test_media.tag_director(movie)
    test_media.tag_genre(movie)
    test_media.tag_label(movie)
    test_media.tag_producer(movie)
    test_media.tag_role(movie)
    test_media.tag_similar(movie)
    test_media.tag_writer(movie)


def test_video_Movie_PlexWebURL(plex, movie):
    url = movie.getWebURL()
    assert url.startswith('https://app.plex.tv/desktop')
    assert plex.machineIdentifier in url
    assert 'details' in url
    assert quote_plus(movie.key) in url
    # Test a different base
    base = 'https://doesnotexist.com/plex'
    url = movie.getWebURL(base=base)
    assert url.startswith(base)


def test_video_Show_attrs(show):
    assert utils.is_datetime(show.addedAt)
    if show.art:
        assert utils.is_art(show.art)
    assert utils.is_int(show.childCount)
    assert show.contentRating in utils.CONTENTRATINGS
    assert utils.is_int(show.duration, gte=1600000)
    # Check reloading the show loads the full list of genres
    show.reload()
    assert utils.is_float(show.audienceRating)
    assert show.audienceRatingImage == "themoviedb://image.rating"
    assert show.audioLanguage == ''
    assert show.autoDeletionItemPolicyUnwatchedLibrary == 0
    assert show.autoDeletionItemPolicyWatchedLibrary == 0
    assert show.enableCreditsMarkerGeneration == -1
    assert show.episodeSort == -1
    assert show.flattenSeasons == -1
    assert "Drama" in [i.tag for i in show.genres]
    assert show.guid == "plex://show/5d9c086c46115600200aa2fe"
    assert "tvdb://121361" in [i.id for i in show.guids]
    # So the initkey should have changed because of the reload
    assert utils.is_metadata(show._initpath)
    assert utils.is_int(show.index)
    assert utils.is_metadata(show.key)
    assert show.languageOverride is None
    assert utils.is_datetime(show.lastRatedAt)
    assert utils.is_datetime(show.lastViewedAt)
    assert utils.is_int(show.leafCount)
    assert show.listType == "video"
    assert len(show.locations) == 1
    assert len(show.locations[0]) >= 10
    assert show.network is None
    assert utils.is_datetime(show.originallyAvailableAt)
    assert show.originalTitle is None
    assert show.rating is None
    if show.ratings:
        assert "themoviedb://image.rating" in [i.image for i in show.ratings]
    assert utils.is_int(show.ratingKey)
    if show.roles:
        assert "Emilia Clarke" in [i.tag for i in show.roles]
        assert show.actors == show.roles
    assert show._server._baseurl == utils.SERVER_BASEURL
    assert utils.is_int(show.seasonCount)
    assert show.showOrdering in (None, 'aired')
    assert show.studio == "Revolution Sun Studios"
    assert utils.is_string(show.summary, gte=100)
    assert show.subtitleLanguage == ''
    assert show.subtitleMode == -1
    assert show.tagline == "Winter is coming."
    assert utils.is_metadata(show.theme, contains="/theme/")
    if show.thumb:
        assert utils.is_thumb(show.thumb)
    assert show.title == "Game of Thrones"
    assert show.titleSort == "Game of Thrones"
    assert show.type == "show"
    assert show.useOriginalTitle == -1
    assert show.userRating is None
    assert utils.is_datetime(show.updatedAt)
    assert utils.is_int(show.viewCount, gte=0)
    assert utils.is_int(show.viewedLeafCount, gte=0)
    assert show.year == 2011
    assert show.url(None) is None


def test_video_Show_episode(show):
    episode = show.episode("Winter Is Coming")
    assert episode == show.episode(season=1, episode=1)
    with pytest.raises(BadRequest):
        show.episode()
    with pytest.raises(NotFound):
        show.episode(season=1337, episode=1337)


def test_video_Show_watched(tvshows):
    show = tvshows.get("The 100")
    episode = show.episodes()[0]
    episode.markPlayed()
    watched = show.watched()
    assert len(watched) == 1 and watched[0].title == "Pilot"
    episode.markUnplayed()


def test_video_Show_unwatched(tvshows):
    show = tvshows.get("The 100")
    episodes = show.episodes()
    episode = episodes[0]
    episode.markPlayed()
    unwatched = show.unwatched()
    assert len(unwatched) == len(episodes) - 1
    episode.markUnplayed()


def test_video_Show_settings(show):
    preferences = show.preferences()
    assert len(preferences) >= 1


def test_video_Show_reload(plex):
    show = plex.library.section("TV Shows").get("Game of Thrones")
    assert utils.is_metadata(show._initpath, prefix="/library/sections/")
    assert len(show.roles) == 3
    show.reload()
    assert utils.is_metadata(show._initpath, prefix="/library/metadata/")
    assert len(show.roles) > 3


def test_video_Show_episodes(tvshows):
    show = tvshows.get("The 100")
    episodes = show.episodes()
    episodes[0].markPlayed()
    unwatched = show.episodes(viewCount=0)
    assert len(unwatched) == len(episodes) - 1


def test_video_Show_download(monkeydownload, tmpdir, show):
    total = len(show.episodes())
    filepaths = show.download(savepath=str(tmpdir))
    assert len(filepaths) == total
    subfolders = show.download(savepath=str(tmpdir), subfolders=True)
    assert len(subfolders) == total


def test_video_Season_download(monkeydownload, tmpdir, show):
    season = show.season(1)
    total = len(season.episodes())
    filepaths = season.download(savepath=str(tmpdir))
    assert len(filepaths) == total


def test_video_Episode_download(monkeydownload, tmpdir, episode):
    filepaths = episode.download(savepath=str(tmpdir))
    assert len(filepaths) == 1
    with_resolution = episode.download(savepath=str(tmpdir), videoResolution="500x300")
    assert len(with_resolution) == 1


# Analyze seems to fail intermittently
@pytest.mark.xfail
def test_video_Show_analyze(show):
    show = show.analyze()


def test_video_Show_markPlayed(show):
    show.markPlayed()
    show.reload()
    assert show.isPlayed


def test_video_Show_markUnplayed(show):
    show.markUnplayed()
    show.reload()
    assert not show.isPlayed


def test_video_Show_refresh(show):
    show.refresh()


def test_video_Show_get(show):
    assert show.get("Winter Is Coming").title == "Winter Is Coming"


def test_video_Show_isPlayed(show):
    assert not show.isPlayed


def test_video_Show_section(show):
    section = show.section()
    assert section.title == "TV Shows"


def test_video_Show_mixins_edit_advanced_settings(show):
    test_mixins.edit_advanced_settings(show)


@pytest.mark.xfail(reason="Changing images fails randomly")
def test_video_Show_mixins_images(show):
    test_mixins.lock_art(show)
    test_mixins.lock_poster(show)
    test_mixins.edit_art(show)
    test_mixins.edit_poster(show)
    test_mixins.attr_artUrl(show)
    test_mixins.attr_posterUrl(show)


def test_video_Show_mixins_themes(show):
    test_mixins.edit_theme(show)


def test_video_Show_mixins_rating(show):
    test_mixins.edit_rating(show)


def test_video_Show_mixins_fields(show):
    test_mixins.edit_added_at(show)
    test_mixins.edit_content_rating(show)
    test_mixins.edit_originally_available(show)
    test_mixins.edit_original_title(show)
    test_mixins.edit_sort_title(show)
    test_mixins.edit_studio(show)
    test_mixins.edit_summary(show)
    test_mixins.edit_tagline(show)
    test_mixins.edit_title(show)


def test_video_Show_mixins_tags(show):
    test_mixins.edit_collection(show)
    test_mixins.edit_genre(show)
    test_mixins.edit_label(show)


def test_video_Show_media_tags(show):
    show.reload()
    test_media.tag_collection(show)
    test_media.tag_genre(show)
    test_media.tag_label(show)
    test_media.tag_role(show)
    test_media.tag_similar(show)


def test_video_Show_PlexWebURL(plex, show):
    url = show.getWebURL()
    assert url.startswith('https://app.plex.tv/desktop')
    assert plex.machineIdentifier in url
    assert 'details' in url
    assert quote_plus(show.key) in url


@pytest.mark.authenticated
def test_video_Show_streamingServices(show):
    assert show.streamingServices()


def test_video_Season(show):
    seasons = show.seasons()
    assert len(seasons) == 2
    assert ["Season 1", "Season 2"] == [s.title for s in seasons[:2]]
    assert show.season("Season 1") == seasons[0]


def test_video_Season_attrs(show):
    season = show.season("Season 1")
    assert utils.is_datetime(season.addedAt)
    if season.art:
        assert utils.is_art(season.art)
    assert season.audioLanguage == ''
    assert season.guid == "plex://season/602e67d31d3358002c411c39"
    assert "tvdb://364731" in [i.id for i in season.guids]
    assert season.index == 1
    assert utils.is_metadata(season._initpath)
    assert utils.is_metadata(season.key)
    assert utils.is_datetime(season.lastRatedAt)
    assert utils.is_datetime(season.lastViewedAt)
    assert utils.is_int(season.leafCount, gte=3)
    assert season.listType == "video"
    assert season.parentGuid == "plex://show/5d9c086c46115600200aa2fe"
    assert season.parentIndex == 1
    assert utils.is_metadata(season.parentKey)
    assert utils.is_int(season.parentRatingKey)
    assert season.parentStudio == "Revolution Sun Studios"
    assert utils.is_metadata(season.parentTheme)
    if season.parentThumb:
        assert utils.is_thumb(season.parentThumb)
    assert season.parentTitle == "Game of Thrones"
    if show.ratings:
        assert "themoviedb://image.rating" in [i.image for i in show.ratings]
    assert utils.is_int(season.ratingKey)
    assert season._server._baseurl == utils.SERVER_BASEURL
    assert utils.is_string(season.summary, gte=100)
    assert season.subtitleLanguage == ''
    assert season.subtitleMode == -1
    if season.thumb:
        assert utils.is_thumb(season.thumb)
    assert season.title == "Season 1"
    assert season.titleSort == "Season 1"
    assert season.type == "season"
    assert utils.is_datetime(season.updatedAt)
    assert utils.is_int(season.viewCount, gte=0)
    assert utils.is_int(season.viewedLeafCount, gte=0)
    assert utils.is_int(season.seasonNumber)
    assert season.year in (None, 2011)


def test_video_Season_show(show):
    season = show.seasons()[0]
    season_by_name = show.season("Season 1")
    assert show.ratingKey == season.parentRatingKey and season_by_name.parentRatingKey
    assert season.ratingKey == season_by_name.ratingKey


def test_video_Season_watched(show):
    season = show.season("Season 1")
    season.markPlayed()
    season.reload()
    assert season.isPlayed


def test_video_Season_unwatched(show):
    season = show.season("Season 1")
    season.markUnplayed()
    season.reload()
    assert not season.isPlayed


def test_video_Season_get(show):
    episode = show.season("Season 1").get("Winter Is Coming")
    assert episode.title == "Winter Is Coming"


def test_video_Season_episode(show):
    season = show.season("Season 1")
    episode = season.get("Winter Is Coming")
    assert episode.title == "Winter Is Coming"
    episode = season.episode(episode=1)
    assert episode.index == 1
    episode = season.episode(1)
    assert episode.index == 1
    with pytest.raises(BadRequest):
        season.episode()


def test_video_Season_episodes(show):
    episodes = show.season("Season 2").episodes()
    assert len(episodes) >= 1


@pytest.mark.xfail(reason="Changing images fails randomly")
def test_video_Season_mixins_images(show):
    season = show.season(season=1)
    test_mixins.lock_art(season)
    test_mixins.lock_poster(season)
    test_mixins.edit_art(season)
    test_mixins.edit_poster(season)
    test_mixins.attr_artUrl(season)
    test_mixins.attr_posterUrl(season)


def test_video_Season_mixins_themes(show):
    season = show.season(season=1)
    test_mixins.attr_themeUrl(season)


def test_video_Season_mixins_rating(show):
    season = show.season(season=1)
    test_mixins.edit_rating(season)


def test_video_Season_mixins_fields(show):
    season = show.season(season=1)
    test_mixins.edit_added_at(season)
    test_mixins.edit_summary(season)
    test_mixins.edit_title(season)


def test_video_Season_mixins_tags(show):
    season = show.season(season=1)
    test_mixins.edit_collection(season)
    test_mixins.edit_label(season)


def test_video_Season_PlexWebURL(plex, season):
    url = season.getWebURL()
    assert url.startswith('https://app.plex.tv/desktop')
    assert plex.machineIdentifier in url
    assert 'details' in url
    assert quote_plus(season.key) in url


def test_video_Episode_updateProgress(episode, patched_http_call):
    episode.updateProgress(2 * 60 * 1000)  # 2 minutes.


def test_video_Episode_updateTimeline(episode, patched_http_call):
    episode.updateTimeline(
        2 * 60 * 1000, state="playing", duration=episode.duration
    )  # 2 minutes.


def test_video_Episode(show):
    episode = show.episode("Winter Is Coming")
    assert episode == show.episode(season=1, episode=1)
    with pytest.raises(BadRequest):
        show.episode()
    with pytest.raises(NotFound):
        show.episode(season=1337, episode=1337)


def test_video_Episode_hidden_season(episode):
    assert episode.skipParent is False
    assert episode.parentRatingKey
    assert episode.parentKey
    assert episode.seasonNumber
    show = episode.show()
    show.editAdvanced(flattenSeasons=1)
    episode.reload()
    assert episode.skipParent is True
    assert episode.parentRatingKey
    assert episode.parentKey
    assert episode.seasonNumber
    show.defaultAdvanced()


def test_video_Episode_parent_weakref(show):
    season = show.season(season=1)
    episode = season.episode(episode=1)
    assert episode._parent is not None
    assert episode._parent() == season
    episode = show.season(season=1).episode(episode=1)
    assert episode._parent is not None
    assert episode._parent() is None


# Analyze seems to fail intermittently
@pytest.mark.xfail
def test_video_Episode_analyze(tvshows):
    episode = tvshows.get("Game of Thrones").episode(season=1, episode=1)
    episode.analyze()


def test_video_Episode_attrs(episode):
    assert utils.is_datetime(episode.addedAt)
    if episode.art:
        assert utils.is_art(episode.art)
    assert utils.is_float(episode.audienceRating)
    assert episode.audienceRatingImage == "themoviedb://image.rating"
    assert episode.contentRating in utils.CONTENTRATINGS
    if episode.directors:
        assert "Timothy Van Patten" in [i.tag for i in episode.directors]
    assert utils.is_int(episode.duration, gte=120000)
    if episode.grandparentArt:
        assert utils.is_art(episode.grandparentArt)
    assert episode.grandparentGuid == "plex://show/5d9c086c46115600200aa2fe"
    assert utils.is_metadata(episode.grandparentKey)
    assert utils.is_int(episode.grandparentRatingKey)
    assert utils.is_metadata(episode.grandparentTheme)
    if episode.grandparentThumb:
        assert utils.is_thumb(episode.grandparentThumb)
    assert episode.grandparentTitle == "Game of Thrones"
    assert episode.guid == "plex://episode/5d9c1275e98e47001eb84029"
    assert "tvdb://3254641" in [i.id for i in episode.guids]
    assert episode.hasPreviewThumbnails is False
    assert episode.index == 1
    assert episode.episodeNumber == episode.index
    assert utils.is_metadata(episode._initpath)
    assert utils.is_metadata(episode.key)
    assert utils.is_datetime(episode.lastRatedAt)
    assert utils.is_datetime(episode.lastViewedAt)
    assert episode.listType == "video"
    assert utils.is_datetime(episode.originallyAvailableAt)
    assert episode.parentGuid == "plex://season/602e67d31d3358002c411c39"
    assert utils.is_int(episode.parentIndex)
    assert episode.seasonNumber == episode.parentIndex
    assert utils.is_metadata(episode.parentKey)
    assert utils.is_int(episode.parentRatingKey)
    if episode.parentThumb:
        assert utils.is_thumb(episode.parentThumb)
    assert episode.parentTitle == "Season 1"
    assert episode.parentYear is None
    if episode.producers:
        assert episode.producers  # Test episode doesn't have producers
    assert episode.rating is None
    if episode.ratings:
        assert "themoviedb://image.rating" in [i.image for i in episode.ratings]
    assert utils.is_int(episode.ratingKey)
    if episode.roles:
        assert "Jason Momoa" in [i.tag for i in episode.roles]
        assert episode.actors == episode.roles
    assert episode._server._baseurl == utils.SERVER_BASEURL
    assert episode.skipParent is False
    assert utils.is_string(episode.summary, gte=100)
    if episode.thumb:
        assert utils.is_thumb(episode.thumb)
    assert episode.title == "Winter Is Coming"
    assert episode.titleSort == "Winter Is Coming"
    assert episode.type == "episode"
    assert utils.is_datetime(episode.updatedAt)
    assert episode.userRating is None
    assert utils.is_int(episode.viewCount, gte=0)
    assert episode.viewOffset == 0
    if episode.writers:
        assert "David Benioff" in [i.tag for i in episode.writers]
    assert episode.year == 2011
    assert episode.isPlayed in [True, False]
    assert len(episode.locations) == 1
    assert len(episode.locations[0]) >= 10
    assert episode.seasonEpisode == "s01e01"
    # Media
    media = episode.media[0]
    assert media.aspectRatio == 1.78
    assert media.audioChannels in utils.AUDIOCHANNELS
    assert media.audioCodec in utils.CODECS
    assert utils.is_int(media.bitrate)
    assert media.container in utils.CONTAINERS
    assert utils.is_int(media.duration, gte=150000)
    assert utils.is_int(media.height, gte=200)
    assert utils.is_int(media.id)
    assert utils.is_metadata(media._initpath)
    if media.optimizedForStreaming:
        assert isinstance(media.optimizedForStreaming, bool)
    assert media._server._baseurl == utils.SERVER_BASEURL
    assert media.videoCodec in utils.CODECS
    assert media.videoFrameRate in utils.FRAMERATES
    assert media.videoResolution in utils.RESOLUTIONS
    assert utils.is_int(media.width, gte=400)
    # Part
    part = media.parts[0]
    assert part.container in utils.CONTAINERS
    assert utils.is_int(part.duration, gte=150000)
    assert len(part.file) >= 10
    assert part.hasPreviewThumbnails is False
    assert utils.is_int(part.id)
    assert utils.is_metadata(part._initpath)
    assert len(part.key) >= 10
    assert part._server._baseurl == utils.SERVER_BASEURL
    assert utils.is_int(part.size, gte=18184197)
    assert part.exists
    assert part.accessible


def test_video_Episode_watched(tvshows):
    season = tvshows.get("The 100").season(1)
    episode = season.episode(1)
    episode.markPlayed()
    watched = season.watched()
    assert len(watched) == 1 and watched[0].title == "Pilot"
    episode.markUnplayed()


def test_video_Episode_unwatched(tvshows):
    season = tvshows.get("The 100").season(1)
    episodes = season.episodes()
    episode = episodes[0]
    episode.markPlayed()
    unwatched = season.unwatched()
    assert len(unwatched) == len(episodes) - 1
    episode.markUnplayed()


@pytest.mark.xfail(reason="Changing images fails randomly")
def test_video_Episode_mixins_images(episode):
    test_mixins.lock_art(episode)
    test_mixins.lock_poster(episode)
    # test_mixins.edit_art(episode)  # Uploading episode artwork is broken in Plex
    test_mixins.edit_poster(episode)
    test_mixins.attr_artUrl(episode)
    test_mixins.attr_posterUrl(episode)


def test_video_Episode_mixins_themes(episode):
    test_mixins.attr_themeUrl(episode)


def test_video_Episode_mixins_rating(episode):
    test_mixins.edit_rating(episode)


def test_video_Episode_mixins_fields(episode):
    test_mixins.edit_added_at(episode)
    test_mixins.edit_content_rating(episode)
    test_mixins.edit_originally_available(episode)
    test_mixins.edit_sort_title(episode)
    test_mixins.edit_summary(episode)
    test_mixins.edit_title(episode)


def test_video_Episode_mixins_tags(episode):
    test_mixins.edit_collection(episode)
    test_mixins.edit_director(episode)
    test_mixins.edit_writer(episode)
    test_mixins.edit_label(episode)


def test_video_Episode_media_tags(episode):
    episode.reload()
    test_media.tag_collection(episode)
    test_media.tag_director(episode)
    test_media.tag_writer(episode)


def test_video_Episode_PlexWebURL(plex, episode):
    url = episode.getWebURL()
    assert url.startswith('https://app.plex.tv/desktop')
    assert plex.machineIdentifier in url
    assert 'details' in url
    assert quote_plus(episode.key) in url


def test_that_reload_return_the_same_object(plex):
    # we want to check this that all the urls are correct
    movie_library_search = plex.library.section("Movies").search("Elephants Dream")[0]
    movie_search = plex.search("Elephants Dream")[0]
    movie_section_get = plex.library.section("Movies").get("Elephants Dream")
    movie_library_search_key = movie_library_search.key
    movie_search_key = movie_search.key
    movie_section_get_key = movie_section_get.key
    assert (
        movie_library_search_key
        == movie_library_search.reload().key
        == movie_search_key
        == movie_search.reload().key
        == movie_section_get_key
        == movie_section_get.reload().key
    )  # noqa
    tvshow_library_search = plex.library.section("TV Shows").search("The 100")[0]
    tvshow_search = plex.search("The 100")[0]
    tvshow_section_get = plex.library.section("TV Shows").get("The 100")
    tvshow_library_search_key = tvshow_library_search.key
    tvshow_search_key = tvshow_search.key
    tvshow_section_get_key = tvshow_section_get.key
    assert (
        tvshow_library_search_key
        == tvshow_library_search.reload().key
        == tvshow_search_key
        == tvshow_search.reload().key
        == tvshow_section_get_key
        == tvshow_section_get.reload().key
    )  # noqa
    season_library_search = tvshow_library_search.season("Season 1")
    season_search = tvshow_search.season("Season 1")
    season_section_get = tvshow_section_get.season("Season 1")
    season_library_search_key = season_library_search.key
    season_search_key = season_search.key
    season_section_get_key = season_section_get.key
    assert (
        season_library_search_key
        == season_library_search.reload().key
        == season_search_key
        == season_search.reload().key
        == season_section_get_key
        == season_section_get.reload().key
    )  # noqa
    episode_library_search = tvshow_library_search.episode(season=1, episode=1)
    episode_search = tvshow_search.episode(season=1, episode=1)
    episode_section_get = tvshow_section_get.episode(season=1, episode=1)
    episode_library_search_key = episode_library_search.key
    episode_search_key = episode_search.key
    episode_section_get_key = episode_section_get.key
    assert (
        episode_library_search_key
        == episode_library_search.reload().key
        == episode_search_key
        == episode_search.reload().key
        == episode_section_get_key
        == episode_section_get.reload().key
    )  # noqa


def test_video_exists_accessible(movie, episode):
    assert movie.media[0].parts[0].exists is None
    assert movie.media[0].parts[0].accessible is None
    movie.reload()
    assert movie.media[0].parts[0].exists is True
    assert movie.media[0].parts[0].accessible is True

    assert episode.media[0].parts[0].exists is None
    assert episode.media[0].parts[0].accessible is None
    episode.reload()
    assert episode.media[0].parts[0].exists is True
    assert episode.media[0].parts[0].accessible is True


def test_video_edits_locked(movie, episode):
    edits = {'titleSort.value': 'New Title Sort', 'titleSort.locked': 1}
    movieTitleSort = movie.titleSort
    movie.edit(**edits)
    movie.reload()
    for field in movie.fields:
        if field.name == 'titleSort':
            assert movie.titleSort == 'New Title Sort'
            assert field.locked is True
    movie.edit(**{'titleSort.value': movieTitleSort, 'titleSort.locked': 0})

    episodeTitleSort = episode.titleSort
    episode.edit(**edits)
    episode.reload()
    for field in episode.fields:
        if field.name == 'titleSort':
            assert episode.titleSort == 'New Title Sort'
            assert field.locked is True
    episode.edit(**{'titleSort.value': episodeTitleSort, 'titleSort.locked': 0})


@pytest.mark.xfail(
    reason="broken? assert len(plex.conversions()) == 1 may fail on some builds"
)
def test_video_optimize(plex, movie, tvshows, show):
    plex.optimizedItems(removeAll=True)
    movie.optimize(target="mobile")
    plex.conversions(pause=True)
    sleep(1)
    assert len(plex.optimizedItems()) == 1
    assert len(plex.conversions()) == 1
    conversion = plex.conversions()[0]
    conversion.remove()
    assert len(plex.conversions()) == 0
    assert len(plex.optimizedItems()) == 1
    optimized = plex.optimizedItems()[0]
    videos = optimized.items()
    assert movie in videos
    plex.optimizedItems(removeAll=True)
    assert len(plex.optimizedItems()) == 0

    locations = tvshows._locations()
    show.optimize(
        deviceProfile="Universal TV",
        videoQuality=VIDEO_QUALITY_3_MBPS_720p,
        locationID=locations[0].id,
        limit=1,
        unwatched=True
    )
    assert len(plex.optimizedItems()) == 1
    plex.optimizedItems(removeAll=True)
    assert len(plex.optimizedItems()) == 0

    with pytest.raises(BadRequest):
        movie.optimize()
    with pytest.raises(BadRequest):
        movie.optimize(target="mobile", locationID=-100)
