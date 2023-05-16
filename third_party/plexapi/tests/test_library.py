# -*- coding: utf-8 -*-
from collections import namedtuple
from datetime import datetime, timedelta
from urllib.parse import quote_plus

import pytest
import plexapi.base
from plexapi.exceptions import BadRequest, NotFound

from . import conftest as utils


def test_library_Library_section(plex):
    sections = plex.library.sections()
    assert len(sections) >= 3
    section_name = plex.library.section("TV Shows")
    assert section_name.title == "TV Shows"
    with pytest.raises(NotFound):
        assert plex.library.section("cant-find-me")
    with pytest.raises(NotFound):
        assert plex.library.sectionByID(-1)


def test_library_Library_sectionByID_is_equal_section(plex, movies):
    # test that sectionByID refreshes the section if the key is missing
    # this is needed if there isn't any cached sections
    assert plex.library.sectionByID(movies.key).uuid == movies.uuid


def test_library_sectionByID_with_attrs(plex, movies):
    assert movies.agent == "tv.plex.agents.movie"
    # This seems to fail for some reason.
    # my account allow of sync, didn't find any about settings about the library.
    # assert movies.allowSync is ("sync" in plex.ownerFeatures)
    assert movies.art == "/:/resources/movie-fanart.jpg"
    assert utils.is_metadata(
        movies.composite, prefix="/library/sections/", contains="/composite/"
    )
    assert utils.is_datetime(movies.createdAt)
    assert movies.filters is True
    assert movies._initpath == "/library/sections"
    assert utils.is_int(movies.key)
    assert movies.language == "en-US"
    assert len(movies.locations) == 1
    assert len(movies.locations[0]) >= 10
    assert movies.refreshing is False
    assert movies.scanner == "Plex Movie"
    assert movies._server._baseurl == utils.SERVER_BASEURL
    assert movies.thumb == "/:/resources/movie.png"
    assert movies.title == "Movies"
    assert movies.type == "movie"
    assert utils.is_datetime(movies.updatedAt)
    assert len(movies.uuid) == 36


def test_library_section_get_movie(movies):
    assert movies.get("Sita Sings the Blues")


def test_library_MovieSection_getGuid(movies, movie):
    result = movies.getGuid(guid=movie.guid)
    assert result == movie
    result = movies.getGuid(guid=movie.guids[0].id)
    assert result == movie
    with pytest.raises(NotFound):
        movies.getGuid(guid='plex://movie/abcdefg')
    with pytest.raises(NotFound):
        movies.getGuid(guid='imdb://tt00000000')


def test_library_section_movies_all(movies):
    assert movies.totalSize == 4
    assert len(movies.all(container_start=0, container_size=1, maxresults=1)) == 1


def test_library_section_movies_all_guids(movies):
    plexapi.base.USER_DONT_RELOAD_FOR_KEYS.add('guids')
    try:
        results = movies.all(includeGuids=False)
        assert results[0].guids == []
        results = movies.all()
        assert results[0].guids
        movie = movies.get("Sita Sings the Blues")
        assert movie.guids
    finally:
        plexapi.base.USER_DONT_RELOAD_FOR_KEYS.remove('guids')


def test_library_section_totalDuration(tvshows):
    assert utils.is_int(tvshows.totalDuration)


def test_library_section_totalStorage(tvshows):
    assert utils.is_int(tvshows.totalStorage)


def test_library_section_totalViewSize(tvshows):
    assert tvshows.totalViewSize() == 2
    assert tvshows.totalViewSize(libtype="show") == 2
    assert tvshows.totalViewSize(libtype="season") == 4
    assert tvshows.totalViewSize(libtype="episode") == 49
    show = tvshows.get("The 100")
    show.addCollection("test_view_size")
    assert tvshows.totalViewSize() == 3
    assert tvshows.totalViewSize(includeCollections=False) == 2
    show.removeCollection("test_view_size", locked=False)


def test_library_section_delete(movies, patched_http_call):
    movies.delete()


def test_library_fetchItem(plex, movie):
    item1 = plex.library.fetchItem(f"/library/metadata/{movie.ratingKey}")
    item2 = plex.library.fetchItem(movie.ratingKey)
    assert item1.title == "Elephants Dream"
    assert item1 == item2 == movie


def test_library_onDeck(plex, movie):
    movie.updateProgress(movie.duration // 4)  # set progress to 25%
    assert movie in plex.library.onDeck()
    movie.markUnplayed()


def test_library_recentlyAdded(plex):
    assert len(list(plex.library.recentlyAdded()))


def test_library_add_edit_delete(plex, movies, photos):
    # Create Other Videos library = No external metadata scanning
    section_name = "plexapi_test_section"
    movie_location = movies.locations[0]
    photo_location = photos.locations[0]
    plex.library.add(
        name=section_name,
        type="movie",
        agent="com.plexapp.agents.none",
        scanner="Plex Video Files Scanner",
        language="xn",
        location=[movie_location, photo_location]
    )
    section = plex.library.section(section_name)
    assert section.title == section_name
    # Create library with an invalid path
    error_section_name = "plexapi_error_section"
    with pytest.raises(BadRequest):
        plex.library.add(
            name=error_section_name,
            type="movie",
            agent="com.plexapp.agents.none",
            scanner="Plex Video Files Scanner",
            language="xn",
            location=[movie_location, photo_location[:-1]]
        )
    # Create library with no path
    with pytest.raises(BadRequest):
        plex.library.add(
            name=error_section_name,
            type="movie",
            agent="com.plexapp.agents.none",
            scanner="Plex Video Files Scanner",
            language="xn",
        )
    with pytest.raises(NotFound):
        plex.library.section(error_section_name)
    new_title = "a renamed lib"
    section.edit(name=new_title)
    section.reload()
    assert section.title == new_title
    with pytest.raises(BadRequest):
        section.addLocations(movie_location[:-1])
    with pytest.raises(BadRequest):
        section.removeLocations(movie_location[:-1])
    section.removeLocations(photo_location)
    section.reload()
    assert len(section.locations) == 1
    section.addLocations(photo_location)
    section.reload()
    assert len(section.locations) == 2
    section.edit(**{'location': movie_location})
    section.reload()
    assert len(section.locations) == 1
    with pytest.raises(BadRequest):
        section.edit(**{'location': movie_location[:-1]})
    # Attempt to remove all locations
    with pytest.raises(BadRequest):
        section.removeLocations(section.locations)
    section.delete()
    assert section not in plex.library.sections()


def test_library_Library_cleanBundle(plex):
    plex.library.cleanBundles()


def test_library_Library_optimize(plex):
    plex.library.optimize()


def test_library_Library_emptyTrash(plex):
    plex.library.emptyTrash()


def _test_library_Library_refresh(plex):
    # TODO: fix mangle and proof the sections attrs
    plex.library.refresh()


def test_library_Library_update(plex):
    plex.library.update()


def test_library_Library_cancelUpdate(plex):
    plex.library.cancelUpdate()


def test_library_Library_deleteMediaPreviews(plex):
    plex.library.deleteMediaPreviews()


def test_library_Library_all(plex):
    assert len(plex.library.all(title__iexact="The 100"))


def test_library_Library_search(plex):
    item = plex.library.search("Elephants Dream")[0]
    assert item.title == "Elephants Dream"
    assert len(plex.library.search(libtype="episode"))


def test_library_Library_tags(plex):
    tags = plex.library.tags('genre')
    assert len(tags)
    with pytest.raises(NotFound):
        plex.library.tags('unknown')


def test_library_MovieSection_update(movies):
    movies.update()


def test_library_MovieSection_update_path(movies):
    movies.update(path=movies.locations[0])


def test_library_MovieSection_refresh(movies, patched_http_call):
    movies.refresh()


def test_library_MovieSection_search_genre(movie, movies):
    genre = movie.genres[0]
    assert len(movies.search(genre=genre)) >= 1


def test_library_MovieSection_cancelUpdate(movies):
    movies.cancelUpdate()


def test_library_deleteMediaPreviews(movies):
    movies.deleteMediaPreviews()


def test_library_MovieSection_onDeck(movie, movies, tvshows, episode):
    movie.updateProgress(movie.duration // 4)  # set progress to 25%
    assert movie in movies.onDeck()
    movie.markUnplayed()
    episode.updateProgress(episode.duration // 4)
    assert episode in tvshows.onDeck()
    episode.markUnplayed()


def test_library_MovieSection_searchMovies(movies):
    assert movies.searchMovies(title="Elephants Dream")


def test_library_MovieSection_recentlyAdded(movies, movie):
    assert movie in movies.recentlyAdded()
    assert movie in movies.recentlyAddedMovies()


def test_library_MovieSection_analyze(movies):
    movies.analyze()


def test_library_MovieSection_collections(movies, movie):
    try:
        collection = movies.createCollection("test_library_MovieSection_collections", movie)
        collections = movies.collections()
        assert len(collections)
        assert collection in collections
        c = movies.collection(collection.title)
        assert collection == c
    finally:
        collection.delete()


def test_library_MovieSection_collection_exception(movies):
    with pytest.raises(NotFound):
        movies.collection("Does Not Exists")


@pytest.mark.authenticated
def test_library_MovieSection_managedHubs(movies):
    recommendations = movies.managedHubs()
    with pytest.raises(BadRequest):
        recommendations[0].remove()
    first = recommendations[0]
    first.promoteRecommended().promoteHome().promoteShared()
    assert first.promotedToRecommended is True
    assert first.promotedToOwnHome is True
    assert first.promotedToSharedHome is True
    first.demoteRecommended().demoteHome().demoteShared()
    assert first.promotedToRecommended is False
    assert first.promotedToOwnHome is False
    assert first.promotedToSharedHome is False
    last = recommendations[-1]
    last.move()
    recommendations = movies.managedHubs()
    assert first.identifier == recommendations[1].identifier
    assert last.identifier == recommendations[0].identifier
    last.move(after=first)
    recommendations = movies.managedHubs()
    assert first.identifier == recommendations[0].identifier
    assert last.identifier == recommendations[1].identifier
    movies.resetManagedHubs()
    recommendations = movies.managedHubs()
    assert first.identifier == recommendations[0].identifier
    assert last.identifier == recommendations[-1].identifier


def test_library_MovieSection_PlexWebURL(plex, movies):
    tab = 'library'
    url = movies.getWebURL(tab=tab)
    assert url.startswith('https://app.plex.tv/desktop')
    assert plex.machineIdentifier in url
    assert f'source={movies.key}' in url
    assert f'pivot={tab}' in url
    # Test a different base
    base = 'https://doesnotexist.com/plex'
    url = movies.getWebURL(base=base)
    assert url.startswith(base)


def test_library_MovieSection_PlexWebURL_hub(plex, movies):
    hubs = movies.hubs()
    hub = next(iter(hubs), None)
    assert hub is not None
    url = hub.section().getWebURL(key=hub.key)
    assert url.startswith('https://app.plex.tv/desktop')
    assert plex.machineIdentifier in url
    assert f'source={movies.key}' in url
    assert quote_plus(hub.key) in url


def test_library_ShowSection_all(tvshows):
    assert len(tvshows.all(title__iexact="The 100"))


def test_library_ShowSection_searchShows(tvshows):
    assert tvshows.searchShows(title="The 100")


def test_library_ShowSection_searchSeasons(tvshows):
    assert tvshows.searchSeasons(**{"show.title": "The 100"})


def test_library_ShowSection_searchEpisodes(tvshows):
    assert tvshows.searchEpisodes(title="Winter Is Coming")


def test_library_ShowSection_recentlyAdded(tvshows, show):
    season = show.season(1)
    episode = season.episode(1)
    assert show in tvshows.recentlyAdded()
    assert show in tvshows.recentlyAddedShows()
    assert season in tvshows.recentlyAddedSeasons()
    assert episode in tvshows.recentlyAddedEpisodes()


def test_library_ShowSection_playlists(tvshows, show):
    episodes = show.episodes()
    try:
        playlist = tvshows.createPlaylist("test_library_ShowSection_playlists", episodes[:3])
        playlists = tvshows.playlists()
        assert len(playlists)
        assert playlist in playlists
        p = tvshows.playlist(playlist.title)
        assert playlist == p
        playlists = tvshows.playlists(title="test_", sort="mediaCount:asc")
        assert playlist in playlists
    finally:
        playlist.delete()


def test_library_ShowSection_playlist_exception(tvshows):
    with pytest.raises(NotFound):
        tvshows.playlist("Does Not Exists")


def test_library_MusicSection_albums(music):
    assert len(music.albums())


def test_library_MusicSection_stations(music):
    assert len(music.stations())


def test_library_MusicSection_searchArtists(music):
    assert len(music.searchArtists(title="Broke for Free"))


def test_library_MusicSection_searchAlbums(music):
    assert len(music.searchAlbums(title="Layers"))


def test_library_MusicSection_searchTracks(music):
    assert len(music.searchTracks(title="As Colourful As Ever"))


def test_library_MusicSection_recentlyAdded(music, artist):
    album = artist.albums()[0]
    track = album.tracks()[0]
    assert artist in music.recentlyAdded()
    assert artist in music.recentlyAddedArtists()
    assert album in music.recentlyAddedAlbums()
    assert track in music.recentlyAddedTracks()


def test_library_PhotoSection_searchAlbums(photos, photoalbum):
    title = photoalbum.title
    albums = photos.searchAlbums(title)
    assert len(albums)


def test_library_PhotoSection_searchPhotos(photos, photoalbum):
    title = photoalbum.photos()[0].title
    assert len(photos.searchPhotos(title))


def test_library_PhotoSection_recentlyAdded(photos, photoalbum):
    assert photoalbum in photos.recentlyAddedAlbums()


def test_library_and_section_search_for_movie(plex, movies):
    find = "Elephants Dream"
    l_search = plex.library.search(find)
    s_search = movies.search(find)
    assert l_search == s_search


def test_library_settings(movies):
    settings = movies.settings()
    assert len(settings) >= 1


def test_library_editAdvanced_default(movies):
    movies.editAdvanced(hidden=2)
    for setting in movies.settings():
        if setting.id == "hidden":
            assert int(setting.value) == 2

    movies.editAdvanced(collectionMode=0)
    for setting in movies.settings():
        if setting.id == "collectionMode":
            assert int(setting.value) == 0

    movies.defaultAdvanced()
    for setting in movies.settings():
        assert str(setting.value) == str(setting.default)


def test_library_lockUnlockAllFields(movies):
    for movie in movies.all():
        assert 'thumb' not in [f.name for f in movie.fields]

    movies.lockAllField('thumb')
    for movie in movies.all():
        assert 'thumb' in [f.name for f in movie.fields]

    movies.unlockAllField('thumb')
    for movie in movies.all():
        assert 'thumb' not in [f.name for f in movie.fields]


def test_search_with_weird_a(plex, tvshows):
    ep_title = "Coup de Grâce"
    result_root = plex.search(ep_title)
    result_shows = tvshows.searchEpisodes(title=ep_title)
    assert result_root
    assert result_shows
    assert result_root == result_shows


def test_crazy_search(plex, movies, movie):
    assert movie in movies.search(
        actor=movie.actors[0], sort="titleSort"
    ), "Unable to search movie by actor."
    assert movie in movies.search(
        director=movie.directors[0]
    ), "Unable to search movie by director."
    assert movie in movies.search(
        year=["2006", "2007"]
    ), "Unable to search movie by year."
    assert movie not in movies.search(year=2007), "Unable to filter movie by year."
    assert movie in movies.search(actor=movie.actors[0].tag)
    assert len(movies.search(container_start=2, maxresults=1)) == 1
    assert len(movies.search(container_size=None)) == 4
    assert len(movies.search(container_size=1)) == 4
    assert len(movies.search(container_start=9999, container_size=1)) == 0
    assert len(movies.search(container_start=2, container_size=1)) == 2


def test_library_section_timeline(plex, movies):
    tl = movies.timeline()
    assert tl.TAG == "LibraryTimeline"
    assert tl.size > 0
    assert tl.allowSync is False
    assert tl.art == "/:/resources/movie-fanart.jpg"
    assert tl.content == "secondary"
    assert tl.identifier == "com.plexapp.plugins.library"
    assert datetime.fromtimestamp(tl.latestEntryTime).date() == datetime.today().date()
    assert tl.mediaTagPrefix == "/system/bundle/media/flags/"
    assert tl.mediaTagVersion > 1
    assert tl.thumb == "/:/resources/movie.png"
    assert tl.title1 == "Movies"
    assert utils.is_int(tl.updateQueueSize, gte=0)
    assert tl.viewGroup == "secondary"
    assert tl.viewMode == 65592


def test_library_MovieSection_hubSearch(movies):
    assert movies.hubSearch("Elephants Dream")


def test_library_MovieSection_search(movies, movie, collection):
    movie.addLabel("test_search")
    movie.addCollection("test_search")
    _test_library_search(movies, movie)
    movie.removeLabel("test_search", locked=False)
    movie.removeCollection("test_search", locked=False)

    _test_library_search(movies, collection)


def test_library_MovieSection_search_FilterChoice(movies, collection):
    filterChoice = next(c for c in movies.listFilterChoices("collection") if c.title == collection.title)
    results = movies.search(filters={'collection': filterChoice})
    movie = collection.items()[0]
    assert movie in results


def test_library_MovieSection_advancedSearch(movies, movie):
    advancedFilters = {
        'and': [
            {
                'or': [
                    {'title': 'elephant'},
                    {'title': 'bunny'}
                ]
            },
            {'year>>': 1990},
            {'unwatched': True}
        ]
    }
    results = movies.search(filters=advancedFilters)
    assert movie in results
    results = movies.search(limit=1)
    assert len(results) == 1


def test_library_ShowSection_search(tvshows, show):
    show.addLabel("test_search")
    show.addCollection("test_search")
    _test_library_search(tvshows, show)
    show.removeLabel("test_search", locked=False)
    show.removeCollection("test_search", locked=False)

    season = show.season(season=1)
    _test_library_search(tvshows, season)

    episode = season.episode(episode=1)
    _test_library_search(tvshows, episode)

    # Additional test for mapping field to the correct libtype
    assert tvshows.search(unwatched=True)  # equal to episode.unwatched=True


def test_library_MusicSection_search(music, artist):
    artist.addGenre("test_search")
    artist.addStyle("test_search")
    artist.addMood("test_search")
    artist.addCollection("test_search")
    _test_library_search(music, artist)
    artist.removeGenre("test_search", locked=False)
    artist.removeStyle("test_search", locked=False)
    artist.removeMood("test_search", locked=False)
    artist.removeCollection("test_search", locked=False)

    album = artist.album("Layers")
    album.addGenre("test_search")
    album.addStyle("test_search")
    album.addMood("test_search")
    album.addCollection("test_search")
    album.addLabel("test_search")
    _test_library_search(music, album)
    album.removeGenre("test_search", locked=False)
    album.removeStyle("test_search", locked=False)
    album.removeMood("test_search", locked=False)
    album.removeCollection("test_search", locked=False)
    album.removeLabel("test_search", locked=False)
    
    track = album.track(track=1)
    track.addMood("test_search")
    _test_library_search(music, track)
    track.removeMood("test_search", locked=False)


def test_library_PhotoSection_search(photos, photoalbum):
    photo = photoalbum.photo("photo1")
    photo.addTag("test_search")
    _test_library_search(photos, photo)
    photo.removeTag("test_search")


def test_library_MovieSection_search_sort(movies):
    results = movies.search(sort="titleSort")
    titleSort = [r.titleSort for r in results]
    assert titleSort == sorted(titleSort)

    results_asc = movies.search(sort="titleSort:asc")
    titleSort_asc = [r.titleSort for r in results_asc]
    assert titleSort == titleSort_asc

    results_desc = movies.search(sort="titleSort:desc")
    titleSort_desc = [r.titleSort for r in results_desc]
    assert titleSort_desc == sorted(titleSort_desc, reverse=True)

    # Test manually added sorts
    results_guid = movies.search(sort="guid")
    guid_asc = [r.guid for r in results_guid]
    assert guid_asc == sorted(guid_asc)

    results_summary = movies.search(sort="summary")
    summary_asc = [r.summary for r in results_summary]
    assert summary_asc == sorted(summary_asc)

    results_tagline = movies.search(sort="tagline")
    tagline_asc = [r.tagline for r in results_tagline if r.tagline]
    assert tagline_asc == sorted(tagline_asc)

    results_updatedAt = movies.search(sort="updatedAt")
    updatedAt_asc = [r.updatedAt for r in results_updatedAt]
    assert updatedAt_asc == sorted(updatedAt_asc)

    # Test multi-sort
    results_multi_str = movies.search(sort="year:asc,titleSort:asc")
    titleSort_multi_str = [(r.year, r.titleSort) for r in results_multi_str]
    assert titleSort_multi_str == sorted(titleSort_multi_str)

    results_multi_list = movies.search(sort=["year:desc", "titleSort:desc"])
    titleSort_multi_list = [(r.year, r.titleSort) for r in results_multi_list]
    assert titleSort_multi_list == sorted(titleSort_multi_list, reverse=True)

    # Test sort using FilteringSort object
    sortObj = next(s for s in movies.listSorts() if s.key == "year")
    results_sortObj = movies.search(sort=sortObj)
    sortObj_list = [r.year for r in results_sortObj]
    assert sortObj_list == sorted(sortObj_list, reverse=True)


def test_library_ShowSection_search_sort(tvshows):
    # Test predefined Plex multi-sort
    seasonAsc = "season.index,season.titleSort"
    results = tvshows.search(sort=seasonAsc, libtype="season")
    sortedResults = sorted(results, key=lambda s: (s.index, s.titleSort))
    assert results == sortedResults

    seasonShowAsc = "show.titleSort,index"
    results = tvshows.search(sort=seasonShowAsc, libtype="season")
    sortedResults = sorted(results, key=lambda s: (s.show().titleSort, s.index))
    assert results == sortedResults

    episodeShowAsc = (
        "show.titleSort,season.index:nullsLast,episode.index:nullsLast,"
        "episode.originallyAvailableAt:nullsLast,episode.titleSort,episode.id"
    )
    results = tvshows.search(sort=episodeShowAsc, libtype="episode")
    sortedResults = sorted(
        results,
        key=lambda e: (
            e.show().titleSort, e.season().index, e.index,
            e.originallyAvailableAt, e.titleSort, e.ratingKey)
    )
    assert results == sortedResults

    episodeShowDesc = (
        "show.titleSort:desc,season.index:nullsLast,episode.index:nullsLast,"
        "episode.originallyAvailableAt:nullsLast,episode.titleSort,episode.id"
    )
    results = tvshows.search(sort=episodeShowDesc, libtype="episode")
    sortedResults = sorted(
        sorted(
            results,
            key=lambda e: (
                e.season().index, e.index,
                e.originallyAvailableAt, e.titleSort, e.ratingKey)
        ),
        key=lambda e: e.show().titleSort,
        reverse=True
    )
    assert results == sortedResults

    # Test manually added sorts
    results_index = tvshows.search(sort="show.index,season.index,episode.index", libtype="episode")
    index_asc = [(r.show().index, r.season().index, r.index) for r in results_index]
    assert index_asc == sorted(index_asc)


def test_library_MusicSection_search_sort(music):
    # Test predefined Plex multi-sort
    albumArtistAsc = "artist.titleSort,album.titleSort,album.index,album.id,album.originallyAvailableAt"
    results = music.search(sort=albumArtistAsc, libtype="album")
    sortedResults = sorted(
        results,
        key=lambda a: (
            a.artist().titleSort, a.titleSort, a.index, a.ratingKey, a.originallyAvailableAt
        )
    )
    assert results == sortedResults

    trackAlbumArtistAsc = (
        "artist.titleSort,album.titleSort,album.year,"
        "track.absoluteIndex,track.index,track.titleSort,track.id"
    )
    results = music.search(sort=trackAlbumArtistAsc, libtype="track")
    sortedResults = sorted(
        results,
        key=lambda t: (
            t.artist().titleSort, t.album().titleSort, t.album().year,
            t.index, t.titleSort, t.ratingKey  # Skip unknown absoluteIndex
        )
    )
    assert results == sortedResults


def test_library_search_exceptions(movies):
    with pytest.raises(BadRequest):
        movies.listFilterChoices(field="123abc.title")
    with pytest.raises(BadRequest):
        movies.search(**{"123abc": True})
    with pytest.raises(BadRequest):
        movies.search(year="123abc")
    with pytest.raises(BadRequest):
        movies.search(sort="123abc")
    with pytest.raises(BadRequest):
        movies.search(filters=[])
    with pytest.raises(BadRequest):
        movies.search(filters={'and': {'title': 'test'}})
    with pytest.raises(BadRequest):
        movies.search(filters={'and': [], 'title': 'test'})
    with pytest.raises(NotFound):
        movies.getFilterType(libtype="show")
    with pytest.raises(NotFound):
        movies.getFieldType(fieldType="unknown")
    with pytest.raises(NotFound):
        movies.listFilterChoices(field="unknown")
    with pytest.raises(NotFound):
        movies.search(unknown="unknown")
    with pytest.raises(NotFound):
        movies.search(**{"title<>!=": "unknown"})
    with pytest.raises(NotFound):
        movies.search(sort="unknown")
    with pytest.raises(NotFound):
        movies.search(sort="titleSort:bad")


def _test_library_search(library, obj):
    # Create & operator
    AndOperator = namedtuple("AndOperator", ["key", "title"])
    andOp = AndOperator("&=", "and")

    fields = library.listFields(obj.type)
    for field in fields:
        fieldAttr = field.key.split(".")[-1]
        operators = library.listOperators(field.type)
        if field.type in {"tag", "string"}:
            operators += [andOp]

        for operator in operators:
            if (
                fieldAttr == "unmatched" and operator.key == "!="
                or fieldAttr in {"audienceRating", "rating"} and operator.key in {"=", "!="}
                or fieldAttr == "userRating"
            ):
                continue

            value = getattr(obj, fieldAttr, None)

            if field.type == "boolean" and value is None:
                value = fieldAttr.startswith("unwatched")
            if field.type == "tag" and isinstance(value, list) and value and operator.title != "and":
                value = value[0]
            elif value is None:
                continue

            if operator.title == "begins with":
                searchValue = value[:3]
            elif operator.title == "ends with":
                searchValue = value[-3:]
            elif "contain" in operator.title:
                searchValue = value.split(" ")[0]
            elif operator.title == "is less than":
                searchValue = value + 1
            elif operator.title == "is greater than":
                searchValue = max(value - 1, 1)
            elif operator.title == "is before":
                searchValue = value + timedelta(days=1)
            elif operator.title == "is after":
                searchValue = value - timedelta(days=1)
            else:
                searchValue = value

            _do_test_library_search(library, obj, field, operator, searchValue)

            # Test search again using string tag and date
            if field.type == "tag" and fieldAttr != "contentRating":
                if not isinstance(searchValue, list):
                    searchValue = [searchValue]
                searchValue = [v.tag for v in searchValue]
                _do_test_library_search(library, obj, field, operator, searchValue)

            elif field.type == "date":
                searchValue = searchValue.strftime("%Y-%m-%d")
                _do_test_library_search(library, obj, field, operator, searchValue)
                searchValue = "1s"
                _do_test_library_search(library, obj, field, operator, searchValue)


def _do_test_library_search(library, obj, field, operator, searchValue):
    searchFilter = {field.key + operator.key[:-1]: searchValue}
    results = library.search(libtype=obj.type, filters=searchFilter)

    if operator.key.startswith("!") or operator.key.startswith(">>") and (searchValue == 1 or searchValue == "1s"):
        assert obj not in results
    else:
        assert obj in results
