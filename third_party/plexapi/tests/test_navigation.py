# -*- coding: utf-8 -*-


def test_navigate_around_show(account, plex):
    show = plex.library.section("TV Shows").get("The 100")
    seasons = show.seasons()
    season = show.season("Season 1")
    episodes = show.episodes()
    episode = show.episode("Pilot")
    assert "Season 1" in [s.title for s in seasons], "Unable to list season:"
    assert "Pilot" in [e.title for e in episodes], "Unable to list episode:"
    assert show.season(season=1) == season
    assert show.season(1) == season
    assert show.episode("Pilot") == episode, "Unable to get show episode:"
    assert season.episode("Pilot") == episode, "Unable to get season episode:"
    assert season.show() == show, "season.show() doesn't match expected show."
    assert episode.show() == show, "episode.show() doesn't match expected show."
    assert episode.season() == season, "episode.season() doesn't match expected season."


def test_navigate_around_artist(account, plex):
    artist = plex.library.section("Music").get("Broke For Free")
    albums = artist.albums()
    album = artist.album("Layers")
    tracks = artist.tracks()
    track = artist.track("As Colourful as Ever")
    print(f"Navigating around artist: {artist}")
    print(f"Album: {album}")
    print(f"Tracks: {tracks}...")
    print(f"Track: {track}")
    assert artist.track("As Colourful as Ever") == track, "Unable to get artist track."
    assert album.track("As Colourful as Ever") == track, "Unable to get album track."
    assert album.artist() == artist, "album.artist() doesn't match expected artist."
    assert track.artist() == artist, "track.artist() doesn't match expected artist."
    assert track.album() == album, "track.album() doesn't match expected album."
