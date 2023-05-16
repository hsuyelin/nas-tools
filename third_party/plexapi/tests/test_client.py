# -*- coding: utf-8 -*-
import time

import pytest


def _check_capabilities(client, capabilities):
    supported = client.protocolCapabilities
    for capability in capabilities:
        if capability not in supported:
            pytest.skip(
                f"Client {client.title} doesn't support {capability} capability support {supported}"
            )


def _check_proxy(plex, client, proxy):
    if proxy:
        client.proxyThroughServer(server=plex)


@pytest.mark.client
def test_list_clients(account, plex):
    assert account.resources(), "MyPlex is not listing any devices."
    assert account.devices(), "MyPlex is not listing any devices."
    assert plex.clients(), "PlexServer is not listing any clients."


@pytest.mark.client
@pytest.mark.parametrize("proxy", [False, True])
def test_client_navigation(plex, client, episode, artist, proxy):

    _check_capabilities(client, ["navigation"])
    client.proxyThroughServer(proxy)
    try:
        print("\nclient.moveUp()")
        client.moveUp()
        time.sleep(0.5)
        print("client.moveLeft()")
        client.moveLeft()
        time.sleep(0.5)
        print("client.moveDown()")
        client.moveDown()
        time.sleep(0.5)
        print("client.moveRight()")
        client.moveRight()
        time.sleep(0.5)
        print("client.select()")
        client.select()
        time.sleep(3)
        print("client.goBack()")
        client.goBack()
        time.sleep(1)
        print("client.goToMedia(episode)")
        client.goToMedia(episode)
        time.sleep(5)
        print("client.goToMedia(artist)")
        client.goToMedia(artist)
        time.sleep(5)
        # print('client.contextMenu'); client.contextMenu(); time.sleep(3)  # socket.timeout
    finally:
        print("client.goToHome()")
        client.goToHome()
        time.sleep(2)


@pytest.mark.client
@pytest.mark.parametrize("proxy", [False, True])
def test_client_playback(plex, client, movies, proxy):

    movie = movies.get("Big buck bunny")

    _check_capabilities(client, ["playback"])
    client.proxyThroughServer(proxy)

    try:
        # Need a movie with subtitles
        mtype = "video"
        subs = [
            stream for stream in movie.subtitleStreams() if stream.language == "English"
        ]
        print(f"client.playMedia({movie.title})")
        client.playMedia(movie)
        time.sleep(5)
        print(f"client.pause({mtype})")
        client.pause(mtype)
        time.sleep(2)
        print(f"client.stepForward({mtype})")
        client.stepForward(mtype)
        time.sleep(5)
        print(f"client.play({mtype})")
        client.play(mtype)
        time.sleep(3)
        print(f"client.stepBack({mtype})")
        client.stepBack(mtype)
        time.sleep(5)
        print(f"client.play({mtype})")
        client.play(mtype)
        time.sleep(3)
        print("client.seekTo(1*60*1000)")
        client.seekTo(1 * 60 * 1000)
        time.sleep(5)
        print("client.setSubtitleStream(0)")
        client.setSubtitleStream(0, mtype)
        time.sleep(10)
        if subs:
            print("client.setSubtitleStream(subs[0])")
            client.setSubtitleStream(subs[0].id, mtype)
        time.sleep(10)
        print(f"client.stop({mtype})")
        client.stop(mtype)
        time.sleep(1)
    finally:
        print("movie.markPlayed")
        movie.markPlayed()
        time.sleep(2)


@pytest.mark.client
@pytest.mark.parametrize("proxy", [False, True])
def test_client_timeline(plex, client, movies, proxy):

    movie = movies.get("Big buck bunny")
    _check_capabilities(client, ["timeline"])
    _check_proxy(plex, client, proxy)
    try:
        # Note: We noticed the isPlaying flag could take up to a full
        # 30 seconds to be updated, hence the long sleeping.
        mtype = "video"
        client.stop(mtype)
        assert client.isPlayingMedia() is False
        print("client.playMedia(movie)")
        client.playMedia(movie)
        time.sleep(10)
        assert client.isPlayingMedia() is True
        print(f"client.stop({mtype})")
        client.stop(mtype)
        time.sleep(10)
        assert client.isPlayingMedia() is False
    finally:
        print("movie.markPlayed()")
        movie.markPlayed()
        time.sleep(2)
