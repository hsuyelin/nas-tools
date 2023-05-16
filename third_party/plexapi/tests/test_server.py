# -*- coding: utf-8 -*-
import re
import time
from urllib.parse import quote_plus

import pytest
from datetime import datetime
from PIL import Image
from plexapi.exceptions import BadRequest, NotFound
from plexapi.server import PlexServer
from plexapi.utils import download
from requests import Session

from . import conftest as utils
from .payloads import SERVER_RESOURCES, SERVER_TRANSCODE_SESSIONS


def test_server_attr(plex, account):
    assert plex._baseurl == utils.SERVER_BASEURL
    assert len(plex.friendlyName) >= 1
    assert len(plex.machineIdentifier) == 40
    assert plex.myPlex is True
    # if you run the tests very shortly after server creation the state in rare cases may be `unknown`
    assert plex.myPlexMappingState in ("mapped", "unknown")
    assert plex.myPlexSigninState == "ok"
    assert utils.is_int(plex.myPlexSubscription, gte=0)
    assert re.match(utils.REGEX_EMAIL, plex.myPlexUsername)
    assert plex.platform in ("Linux", "Windows")
    assert len(plex.platformVersion) >= 5
    assert plex._token == account.authenticationToken
    assert utils.is_int(plex.transcoderActiveVideoSessions, gte=0)
    assert utils.is_datetime(plex.updatedAt)
    assert len(plex.version) >= 5


def test_server_alert_listener(plex, movies):
    try:
        messages = []
        listener = plex.startAlertListener(messages.append)
        movies.refresh()
        utils.wait_until(lambda: len(messages) >= 3, delay=1, timeout=30)
        assert len(messages) >= 3
    finally:
        listener.stop()


@pytest.mark.req_client
def test_server_session():
    # TODO: Implement test_server_session
    pass


def test_server_library(plex):
    # TODO: Implement test_server_library
    assert plex.library


def test_server_url(plex):
    assert "ohno" in plex.url("ohno")


def test_server_transcodeImage(tmpdir, plex, movie):
    width, height = 500, 100
    background = "000000"
    blend = "FFFFFF"

    original_url = movie.thumbUrl
    resize_jpeg_url = plex.transcodeImage(original_url, height, width)
    no_minSize_png_url = plex.transcodeImage(original_url, height, width, minSize=False, imageFormat="png")
    grayscale_url = plex.transcodeImage(original_url, height, width, saturation=0)
    opacity_background_url = plex.transcodeImage(original_url, height, width, opacity=0, background=background, blur=100)
    blend_url = plex.transcodeImage(original_url, height, width, blendColor=blend, blur=1000)
    online_no_upscale_url = plex.transcodeImage(
        "https://raw.githubusercontent.com/pkkid/python-plexapi/master/tests/data/cute_cat.jpg", 1000, 1000, upscale=False)

    original_img = download(
        original_url, plex._token, savepath=str(tmpdir), filename="original_img",
    )
    resized_jpeg_img = download(
        resize_jpeg_url, plex._token, savepath=str(tmpdir), filename="resized_jpeg_img"
    )
    no_minSize_png_img = download(
        no_minSize_png_url, plex._token, savepath=str(tmpdir), filename="no_minSize_png_img"
    )
    grayscale_img = download(
        grayscale_url, plex._token, savepath=str(tmpdir), filename="grayscale_img"
    )
    opacity_background_img = download(
        opacity_background_url, plex._token, savepath=str(tmpdir), filename="opacity_background_img"
    )
    blend_img = download(
        blend_url, plex._token, savepath=str(tmpdir), filename="blend_img"
    )
    online_no_upscale_img = download(
        online_no_upscale_url, plex._token, savepath=str(tmpdir), filename="online_no_upscale_img"
    )

    with Image.open(original_img) as image:
        assert image.size[0] != width
        assert image.size[1] != height
    with Image.open(resized_jpeg_img) as image:
        assert image.size[0] == width
        assert image.size[1] != height
        assert image.format == "JPEG"
    with Image.open(no_minSize_png_img) as image:
        assert image.size[0] != width
        assert image.size[1] == height
        assert image.format == "PNG"
    assert utils.detect_color_image(grayscale_img) == "grayscale"
    assert utils.detect_dominant_hexcolor(opacity_background_img) == background
    assert utils.detect_color_distance(utils.detect_dominant_hexcolor(blend_img), blend)
    with Image.open(online_no_upscale_img) as image1:
        with Image.open(utils.STUB_IMAGE_PATH) as image2:
            assert image1.size == image2.size


def test_server_fetchitem_notfound(plex):
    with pytest.raises(NotFound):
        plex.fetchItem(123456789)


def test_server_search(plex, movie):
    title = movie.title
    #  this search seem to fail on my computer but not at travis, wtf.
    assert plex.search(title)
    results = plex.search(title, mediatype="movie")
    assert results[0] == movie
    # Test genre search
    genre = movie.genres[0]
    results = plex.search(genre.tag, mediatype="genre")
    hub_tag = results[0]
    assert utils.is_int(hub_tag.count)
    assert hub_tag.filter == f"genre={hub_tag.id}"
    assert utils.is_int(hub_tag.id)
    assert utils.is_metadata(
        hub_tag.key,
        prefix=hub_tag.librarySectionKey,
        contains=f"{hub_tag.librarySectionID}/all",
        suffix=hub_tag.filter)
    assert utils.is_int(hub_tag.librarySectionID)
    assert utils.is_metadata(hub_tag.librarySectionKey, prefix="/library/sections")
    assert hub_tag.librarySectionTitle == "Movies"
    assert hub_tag.librarySectionType == 1
    assert hub_tag.reason == "section"
    assert hub_tag.reasonID == hub_tag.librarySectionID
    assert hub_tag.reasonTitle == hub_tag.librarySectionTitle
    assert hub_tag.type == "tag"
    assert hub_tag.tag == genre.tag
    assert hub_tag.tagType == 1
    assert hub_tag.tagValue is None
    assert hub_tag.thumb is None
    assert movie in hub_tag.items()
    # Test director search
    director = movie.directors[0]
    assert plex.search(director.tag, mediatype="director")
    # Test actor search
    role = movie.roles[0]
    assert plex.search(role.tag, mediatype="actor")


def test_server_playlist(plex, show):
    episodes = show.episodes()
    playlist = plex.createPlaylist("test_playlist", items=episodes[:3])
    try:
        assert playlist.title == "test_playlist"
        with pytest.raises(NotFound):
            plex.playlist("<playlist-not-found>")
    finally:
        playlist.delete()


def test_server_playlists(plex, show):
    playlists = plex.playlists()
    count = len(playlists)
    episodes = show.episodes()
    playlist = plex.createPlaylist("test_playlist", items=episodes[:3])
    try:
        playlists = plex.playlists()
        assert len(playlists) == count + 1
        assert playlist in plex.playlists(playlistType='video')
        assert playlist not in plex.playlists(playlistType='audio')
    finally:
        playlist.delete()


def test_server_history(plex, movie):
    movie.markPlayed()
    history = plex.history()
    assert len(history)
    movie.markUnplayed()


def test_server_Server_query(plex):
    assert plex.query("/")
    with pytest.raises(NotFound):
        assert plex.query("/asdf/1234/asdf", headers={"random_headers": "1234"})


def test_server_Server_session(account):
    # Mock Session
    class MySession(Session):
        def __init__(self):
            super(self.__class__, self).__init__()
            self.plexapi_session_test = True

    # Test Code
    plex = PlexServer(
        utils.SERVER_BASEURL, account.authenticationToken, session=MySession()
    )
    assert hasattr(plex._session, "plexapi_session_test")


@pytest.mark.authenticated
def test_server_token_in_headers(plex):
    headers = plex._headers()
    assert "X-Plex-Token" in headers
    assert len(headers["X-Plex-Token"]) >= 1


def test_server_createPlayQueue(plex, movie):
    playqueue = plex.createPlayQueue(movie, shuffle=1, repeat=1)
    assert "shuffle=1" in playqueue._initpath
    assert "repeat=1" in playqueue._initpath
    assert playqueue.playQueueShuffled is True


def test_server_client_not_found(plex):
    with pytest.raises(NotFound):
        plex.client("<This-client-should-not-be-found>")


def test_server_sessions(plex):
    assert len(plex.sessions()) >= 0


def test_server_butlerTasks(plex):
    assert len(plex.butlerTasks())


def test_server_runButlerTask(plex):
    assert plex.runButlerTask("CleanOldBundles")
    with pytest.raises(BadRequest):
        plex.runButlerTask("<This-task-should-not-exist>")


def test_server_isLatest(plex, mocker):
    from os import environ

    is_latest = plex.isLatest()
    if environ.get("PLEX_CONTAINER_TAG") and environ["PLEX_CONTAINER_TAG"] != "latest":
        assert not is_latest
    else:
        return pytest.skip(
            "Do not forget to run with PLEX_CONTAINER_TAG != latest to ensure that update is available"
        )


def test_server_installUpdate(plex, mocker):
    m = mocker.MagicMock(release="aa")
    with utils.patch('plexapi.server.PlexServer.checkForUpdate', return_value=m):
        with utils.callable_http_patch():
            plex.installUpdate()


def test_server_checkForUpdate(plex, mocker):
    class R:
        def __init__(self, **kwargs):
            self.download_key = "plex.tv/release/1337"
            self.version = "1337"
            self.added = "gpu transcode"
            self.fixed = "fixed rare bug"
            self.downloadURL = "http://path-to-update"
            self.state = "downloaded"

    with utils.patch('plexapi.server.PlexServer.checkForUpdate', return_value=R()):
        rel = plex.checkForUpdate(force=False, download=True)
        assert rel.download_key == "plex.tv/release/1337"
        assert rel.version == "1337"
        assert rel.added == "gpu transcode"
        assert rel.fixed == "fixed rare bug"
        assert rel.downloadURL == "http://path-to-update"
        assert rel.state == "downloaded"


@pytest.mark.client
def test_server_clients(plex):
    assert len(plex.clients())
    client = plex.clients()[0]
    assert client._baseurl == utils.CLIENT_BASEURL
    assert client._server._baseurl == utils.SERVER_BASEURL
    assert client.protocol == 'plex'
    assert int(client.protocolVersion) in range(4)
    assert isinstance(client.machineIdentifier, str)
    assert client.deviceClass in ['phone', 'tablet', 'stb', 'tv', 'pc']
    assert set(client.protocolCapabilities).issubset({'timeline', 'playback', 'navigation', 'mirror', 'playqueues'})


@pytest.mark.authenticated
@pytest.mark.xfail(strict=False)
def test_server_account(plex):
    account = plex.account()
    assert account.authToken
    # TODO: Figure out why this is missing from time to time.
    # assert account.mappingError == 'publisherror'
    assert account.mappingErrorMessage is None
    assert account.mappingState == "mapped"
    if account.mappingError != "unreachable":
        if account.privateAddress is not None:
            # This seems to fail way to often..
            if len(account.privateAddress):
                assert re.match(utils.REGEX_IPADDR, account.privateAddress)
            else:
                assert account.privateAddress == ""

        assert int(account.privatePort) >= 1000
        assert re.match(utils.REGEX_IPADDR, account.publicAddress)
        assert int(account.publicPort) >= 1000
    else:
        assert account.privateAddress == ""
        assert int(account.privatePort) == 0
        assert account.publicAddress == ""
        assert int(account.publicPort) == 0
    assert account.signInState == "ok"
    assert isinstance(account.subscriptionActive, bool)
    if account.subscriptionActive:
        assert len(account.subscriptionFeatures)
    # Below check keeps failing.. it should go away.
    # else: assert sorted(account.subscriptionFeatures) == ['adaptive_bitrate',
    #     'download_certificates', 'federated-auth', 'news']
    assert (
        account.subscriptionState == "Active"
        if account.subscriptionActive
        else "Unknown"
    )
    assert re.match(utils.REGEX_EMAIL, account.username)


@pytest.mark.authenticated
def test_server_claim_unclaim(plex, account):
    server_account = plex.account()
    assert server_account.signInState == 'ok'
    result = plex.unclaim()
    assert result.signInState == 'none'
    result = plex.claim(account)
    assert result.signInState == 'ok'


def test_server_downloadLogs(tmpdir, plex):
    plex.downloadLogs(savepath=str(tmpdir), unpack=True)
    assert len(tmpdir.listdir()) > 1


def test_server_downloadDatabases(tmpdir, plex):
    plex.downloadDatabases(savepath=str(tmpdir), unpack=True)
    assert len(tmpdir.listdir()) > 1


def test_server_browse(plex, movies):
    movies_path = movies.locations[0]
    # browse root
    paths = plex.browse()
    assert len(paths)
    # browse the path of the movie library
    paths = plex.browse(movies_path)
    assert len(paths)
    # browse the path of the movie library without files
    paths = plex.browse(movies_path, includeFiles=False)
    assert not len([f for f in paths if f.TAG == 'File'])
    # walk the path of the movie library
    for path, paths, files in plex.walk(movies_path):
        assert path.startswith(movies_path)
        assert len(paths) or len(files)


def test_server_allowMediaDeletion(account):
    plex = PlexServer(utils.SERVER_BASEURL, account.authenticationToken)
    # Check server current allowMediaDeletion setting
    if plex.allowMediaDeletion:
        # If allowed then test disallowed
        plex._allowMediaDeletion(False)
        time.sleep(1)
        plex = PlexServer(utils.SERVER_BASEURL, account.authenticationToken)
        assert plex.allowMediaDeletion is None
        # Test redundant toggle
        with pytest.raises(BadRequest):
            plex._allowMediaDeletion(False)

        plex._allowMediaDeletion(True)
        time.sleep(1)
        plex = PlexServer(utils.SERVER_BASEURL, account.authenticationToken)
        assert plex.allowMediaDeletion is True
        # Test redundant toggle
        with pytest.raises(BadRequest):
            plex._allowMediaDeletion(True)
    else:
        # If disallowed then test allowed
        plex._allowMediaDeletion(True)
        time.sleep(1)
        plex = PlexServer(utils.SERVER_BASEURL, account.authenticationToken)
        assert plex.allowMediaDeletion is True
        # Test redundant toggle
        with pytest.raises(BadRequest):
            plex._allowMediaDeletion(True)

        plex._allowMediaDeletion(False)
        time.sleep(1)
        plex = PlexServer(utils.SERVER_BASEURL, account.authenticationToken)
        assert plex.allowMediaDeletion is None
        # Test redundant toggle
        with pytest.raises(BadRequest):
            plex._allowMediaDeletion(False)


def test_server_system_accounts(plex):
    accounts = plex.systemAccounts()
    assert len(accounts)
    account = accounts[-1]
    assert utils.is_bool(account.autoSelectAudio)
    assert account.defaultAudioLanguage == "en"
    assert account.defaultSubtitleLanguage == "en"
    assert utils.is_int(account.id, gte=0)
    assert len(account.key)
    assert len(account.name)
    assert account.subtitleMode == 0
    assert account.thumb == ""
    assert account.accountID == account.id
    assert account.accountKey == account.key
    assert plex.systemAccount(account.id) == account


def test_server_system_devices(plex):
    devices = plex.systemDevices()
    assert len(devices)
    device = devices[-1]
    assert device.clientIdentifier or device.clientIdentifier == ""
    assert utils.is_datetime(device.createdAt)
    assert utils.is_int(device.id)
    assert len(device.key)
    assert len(device.name) or device.name == ""
    assert len(device.platform) or device.platform == ""
    assert plex.systemDevice(device.id) == device
    

@pytest.mark.authenticated
def test_server_dashboard_bandwidth(plex):
    bandwidthData = plex.bandwidth()
    assert len(bandwidthData)
    bandwidth = bandwidthData[0]
    assert utils.is_int(bandwidth.accountID, gte=0)
    assert utils.is_datetime(bandwidth.at)
    assert utils.is_int(bandwidth.bytes)
    assert utils.is_int(bandwidth.deviceID)
    assert utils.is_bool(bandwidth.lan)
    assert bandwidth.timespan == 6  # Default seconds timespan
    account = bandwidth.account()
    assert utils.is_int(account.id, gte=0)
    device = bandwidth.device()
    assert utils.is_int(device.id)


@pytest.mark.authenticated
def test_server_dashboard_bandwidth_filters(plex):
    at = datetime(2021, 1, 1)
    filters = {
        'at>': at,
        'bytes>': 1,
        'lan': True,
        'accountID': 1
    }
    bandwidthData = plex.bandwidth(timespan='hours', **filters)
    assert len(bandwidthData)
    bandwidth = bandwidthData[0]
    assert bandwidth.accountID == 1
    assert bandwidth.at >= at
    assert bandwidth.bytes >= 1
    assert bandwidth.lan is True
    assert bandwidth.timespan == 4
    with pytest.raises(BadRequest):
        plex.bandwidth(timespan='n/a')
    with pytest.raises(BadRequest):
        filters = {'n/a': None}
        plex.bandwidth(**filters)
    with pytest.raises(BadRequest):
        filters = {'at': 123456}
        plex.bandwidth(**filters)


@pytest.mark.authenticated
def test_server_dashboard_resources(plex, requests_mock):
    url = plex.url("/statistics/resources")
    requests_mock.get(url, text=SERVER_RESOURCES)
    resourceData = plex.resources()
    assert len(resourceData)
    resource = resourceData[0]
    assert utils.is_datetime(resource.at)
    assert utils.is_float(resource.hostCpuUtilization, gte=0.0)
    assert utils.is_float(resource.hostMemoryUtilization, gte=0.0)
    assert utils.is_float(resource.processCpuUtilization, gte=0.0)
    assert utils.is_float(resource.processMemoryUtilization, gte=0.0)
    assert resource.timespan == 6  # Default seconds timespan


def test_server_transcode_sessions(plex, requests_mock):
    url = plex.url("/transcode/sessions")
    requests_mock.get(url, text=SERVER_TRANSCODE_SESSIONS)
    transcode_sessions = plex.transcodeSessions()
    assert len(transcode_sessions)
    session = transcode_sessions[0]
    assert session.audioChannels == 2
    assert session.audioCodec in utils.CODECS
    assert session.audioDecision == "transcode"
    assert session.complete is False
    assert session.container in utils.CONTAINERS
    assert session.context == "streaming"
    assert utils.is_int(session.duration, gte=100000)
    assert utils.is_int(session.height, gte=480)
    assert len(session.key)
    assert utils.is_float(session.maxOffsetAvailable, gte=0.0)
    assert utils.is_float(session.minOffsetAvailable, gte=0.0)
    assert utils.is_float(session.progress)
    assert session.protocol == "dash"
    assert utils.is_int(session.remaining)
    assert utils.is_int(session.size)
    assert session.sourceAudioCodec in utils.CODECS
    assert session.sourceVideoCodec in utils.CODECS
    assert utils.is_float(session.speed)
    assert session.subtitleDecision is None
    assert session.throttled is False
    assert utils.is_float(session.timestamp, gte=1600000000)
    assert session.transcodeHwDecoding in utils.HW_DECODERS
    assert session.transcodeHwDecodingTitle == "Windows (DXVA2)"
    assert session.transcodeHwEncoding in utils.HW_ENCODERS
    assert session.transcodeHwEncodingTitle == "Intel (QuickSync)"
    assert session.transcodeHwFullPipeline is False
    assert session.transcodeHwRequested is True
    assert session.videoCodec in utils.CODECS
    assert session.videoDecision == "transcode"
    assert utils.is_int(session.width, gte=852)


def test_server_PlexWebURL(plex):
    url = plex.getWebURL()
    assert url.startswith('https://app.plex.tv/desktop')
    assert plex.machineIdentifier in url
    assert quote_plus('/hubs') in url
    assert 'pageType=hub' in url
    # Test a different base
    base = 'https://doesnotexist.com/plex'
    url = plex.getWebURL(base=base)
    assert url.startswith(base)


def test_server_PlexWebURL_playlists(plex):
    tab = 'audio'
    url = plex.getWebURL(playlistTab=tab)
    assert url.startswith('https://app.plex.tv/desktop')
    assert plex.machineIdentifier in url
    assert 'source=playlists' in url
    assert f'pivot=playlists.{tab}' in url


def test_server_agents(plex):
    agents = plex.agents()
    assert agents
    agent = next((a for a in agents if a.identifier == 'com.plexapp.agents.imdb'), None)
    assert agent
    settings = agent.settings()
    assert settings
    setting = next((s for s in settings if s.id == 'country'), None)
    assert setting
    assert setting.enumValues is not None
