# -*- coding: utf-8 -*-
import math
import os
import time
from datetime import datetime
from functools import partial

import plexapi
import pytest
import requests
from PIL import Image, ImageColor, ImageStat
from plexapi.client import PlexClient
from plexapi.exceptions import NotFound
from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
from plexapi.utils import createMyPlexDevice

from .payloads import ACCOUNT_XML

try:
    from unittest.mock import patch, MagicMock, mock_open
except ImportError:
    from mock import patch, MagicMock, mock_open


SERVER_BASEURL = plexapi.CONFIG.get("auth.server_baseurl")
MYPLEX_USERNAME = plexapi.CONFIG.get("auth.myplex_username")
MYPLEX_PASSWORD = plexapi.CONFIG.get("auth.myplex_password")
SERVER_TOKEN = plexapi.CONFIG.get("auth.server_token")
CLIENT_BASEURL = plexapi.CONFIG.get("auth.client_baseurl")
CLIENT_TOKEN = plexapi.CONFIG.get("auth.client_token")

MIN_DATETIME = datetime(1999, 1, 1)
REGEX_EMAIL = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
REGEX_IPADDR = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"

AUDIOCHANNELS = {2, 6}
AUDIOLAYOUTS = {"5.1", "5.1(side)", "stereo"}
CODECS = {"aac", "ac3", "dca", "h264", "mp3", "mpeg4"}
CONTAINERS = {"avi", "mp4", "mkv"}
CONTENTRATINGS = {"TV-14", "TV-MA", "G", "NR", "Not Rated"}
FRAMERATES = {"24p", "PAL", "NTSC"}
PROFILES = {"advanced simple", "main", "constrained baseline"}
RESOLUTIONS = {"sd", "480", "576", "720", "1080"}
HW_DECODERS = {'dxva2', 'videotoolbox', 'mediacodecndk', 'vaapi', 'nvdec'}
HW_ENCODERS = {'qsv', 'mf', 'videotoolbox', 'mediacodecndk', 'vaapi', 'nvenc', 'x264'}
ENTITLEMENTS = {
    "ios",
    "roku",
    "android",
    "xbox_one",
    "xbox_360",
    "windows",
    "windows_phone",
}
SYNC_DEVICE_IDENTIFIER = f"test-sync-client-{plexapi.X_PLEX_IDENTIFIER}"
SYNC_DEVICE_HEADERS = {
    "X-Plex-Provides": "sync-target",
    "X-Plex-Platform": "iOS",
    "X-Plex-Platform-Version": "11.4.1",
    "X-Plex-Device": "iPhone",
    "X-Plex-Device-Name": "Test Sync Device",
    "X-Plex-Client-Identifier": SYNC_DEVICE_IDENTIFIER
}

TEST_AUTHENTICATED = "authenticated"
TEST_ANONYMOUSLY = "anonymously"
ANON_PARAM = pytest.param(TEST_ANONYMOUSLY, marks=pytest.mark.anonymous)
AUTH_PARAM = pytest.param(TEST_AUTHENTICATED, marks=pytest.mark.authenticated)

BASE_DIR_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUB_MOVIE_PATH = os.path.join(BASE_DIR_PATH, "tests", "data", "video_stub.mp4")
STUB_MP3_PATH = os.path.join(BASE_DIR_PATH, "tests", "data", "audio_stub.mp3")
STUB_IMAGE_PATH = os.path.join(BASE_DIR_PATH, "tests", "data", "cute_cat.jpg")


def pytest_addoption(parser):
    parser.addoption(
        "--client", action="store_true", default=False, help="Run client tests."
    )


def pytest_generate_tests(metafunc):
    if "plex" in metafunc.fixturenames:
        if (
            "account" in metafunc.fixturenames
            or TEST_AUTHENTICATED in metafunc.definition.keywords
        ):
            metafunc.parametrize("plex", [AUTH_PARAM], indirect=True)
        else:
            metafunc.parametrize("plex", [ANON_PARAM, AUTH_PARAM], indirect=True)
    elif "account" in metafunc.fixturenames:
        metafunc.parametrize("account", [AUTH_PARAM], indirect=True)


def pytest_runtest_setup(item):
    if "client" in item.keywords and not item.config.getvalue("client"):
        return pytest.skip("Need --client option to run.")
    if TEST_AUTHENTICATED in item.keywords and not (
        MYPLEX_USERNAME and MYPLEX_PASSWORD or SERVER_TOKEN
    ):
        return pytest.skip(
            "You have to specify MYPLEX_USERNAME and MYPLEX_PASSWORD or SERVER_TOKEN to run authenticated tests"
        )
    if TEST_ANONYMOUSLY in item.keywords and (MYPLEX_USERNAME and MYPLEX_PASSWORD or SERVER_TOKEN):
        return pytest.skip(
            "Anonymous tests should be ran on unclaimed server, without providing MYPLEX_USERNAME and "
            "MYPLEX_PASSWORD or SERVER_TOKEN"
        )


# ---------------------------------
#  Fixtures
# ---------------------------------


@pytest.fixture(scope="session")
def sess():
    session = requests.Session()
    session.request = partial(session.request, timeout=120)
    return session


@pytest.fixture(scope="session")
def account(sess):
    if SERVER_TOKEN:
        return MyPlexAccount(session=sess)
    assert MYPLEX_USERNAME, "Required MYPLEX_USERNAME not specified."
    assert MYPLEX_PASSWORD, "Required MYPLEX_PASSWORD not specified."
    return MyPlexAccount(session=sess)


@pytest.fixture(scope="session")
def account_once(account):
    if os.environ.get("TEST_ACCOUNT_ONCE") not in ("1", "true") and os.environ.get("CI") == "true":
        pytest.skip("Do not forget to test this by providing TEST_ACCOUNT_ONCE=1")
    return account


@pytest.fixture(scope="session")
def account_plexpass(account):
    if not account.subscriptionActive:
        pytest.skip(
            "PlexPass subscription is not active, unable to test sync-stuff, be careful!"
        )
    return account


@pytest.fixture(scope="session")
def account_synctarget(account_plexpass):
    assert "sync-target" in SYNC_DEVICE_HEADERS["X-Plex-Provides"]
    assert "iOS" == SYNC_DEVICE_HEADERS["X-Plex-Platform"]
    assert "11.4.1" == SYNC_DEVICE_HEADERS["X-Plex-Platform-Version"]
    assert "iPhone" == SYNC_DEVICE_HEADERS["X-Plex-Device"]
    return account_plexpass


@pytest.fixture()
def mocked_account(requests_mock):
    requests_mock.get("https://plex.tv/users/account", text=ACCOUNT_XML)
    return MyPlexAccount(token="faketoken")


@pytest.fixture(scope="session")
def plex(request, sess):
    assert SERVER_BASEURL, "Required SERVER_BASEURL not specified."

    if request.param == TEST_AUTHENTICATED:
        token = MyPlexAccount(session=sess).authenticationToken
    else:
        token = None
    return PlexServer(SERVER_BASEURL, token, session=sess)


@pytest.fixture(scope="session")
def sync_device(account_synctarget):
    try:
        device = account_synctarget.device(clientId=SYNC_DEVICE_IDENTIFIER)
    except NotFound:
        device = createMyPlexDevice(SYNC_DEVICE_HEADERS, account_synctarget)

    assert device
    assert "sync-target" in device.provides
    return device


@pytest.fixture()
def clear_sync_device(sync_device, plex):
    sync_items = sync_device.syncItems()
    for item in sync_items.items:
        item.delete()
    plex.refreshSync()
    return sync_device


@pytest.fixture
def fresh_plex():
    return PlexServer


@pytest.fixture()
def plex2(plex):
    return plex()


@pytest.fixture()
def client(request, plex):
    return PlexClient(plex, baseurl=CLIENT_BASEURL, token=CLIENT_TOKEN)


@pytest.fixture()
def movies(plex):
    return plex.library.section("Movies")


@pytest.fixture()
def tvshows(plex):
    return plex.library.section("TV Shows")


@pytest.fixture()
def music(plex):
    return plex.library.section("Music")


@pytest.fixture()
def photos(plex):
    return plex.library.section("Photos")


@pytest.fixture()
def movie(movies):
    return movies.get("Elephants Dream")


@pytest.fixture()
def show(tvshows):
    return tvshows.get("Game of Thrones")


@pytest.fixture()
def season(show):
    return show.season(1)


@pytest.fixture()
def episode(season):
    return season.get("Winter Is Coming")


@pytest.fixture()
def artist(music):
    return music.get("Broke For Free")


@pytest.fixture()
def album(artist):
    return artist.album("Layers")


@pytest.fixture()
def track(album):
    return album.track("As Colourful as Ever")


@pytest.fixture()
def photoalbum(photos):
    try:
        return photos.get("Cats")
    except Exception:
        return photos.get("photo_album1")


@pytest.fixture()
def photo(photoalbum):
    return photoalbum.photo("photo1")


@pytest.fixture()
def collection(plex, movies, movie):
    try:
        return movies.collection("Test Collection")
    except NotFound:
        return plex.createCollection(
            title="Test Collection",
            section=movies,
            items=movie
        )


@pytest.fixture()
def playlist(plex, tvshows, season):
    try:
        return tvshows.playlist("Test Playlist")
    except NotFound:
        return plex.createPlaylist(
            title="Test Playlist",
            items=season.episodes()[:3]
        )


@pytest.fixture()
def subtitle():
    mopen = mock_open()
    with patch("__main__.open", mopen):
        with open("subtitle.srt", "w") as handler:
            handler.write("test")
        return handler


@pytest.fixture()
def m3ufile(plex, music, track, tmp_path):
    for path, paths, files in plex.walk(music.locations[0]):
        for file in files:
            if file.title == "playlist.m3u":
                return file.path
    m3u = tmp_path / "playlist.m3u"
    with open(m3u, "w") as handler:
        handler.write(track.media[0].parts[0].file)
    return str(m3u)


@pytest.fixture()
def shared_username(account):
    username = os.environ.get("SHARED_USERNAME", "PKKid")
    for user in account.users():
        if user.title.lower() == username.lower():
            return username
        elif (
            user.username
            and user.email
            and user.id
            and username.lower()
            in (user.username.lower(), user.email.lower(), str(user.id))
        ):
            return username
    pytest.skip(f"Shared user {username} wasn't found in your MyPlex account")


@pytest.fixture()
def monkeydownload(request, monkeypatch):
    monkeypatch.setattr(
        "plexapi.utils.download", partial(plexapi.utils.download, mocked=True)
    )
    yield
    monkeypatch.undo()


def callable_http_patch():
    """This is intended to stop some http requests inside some tests."""
    return patch(
        "plexapi.server.requests.sessions.Session.send",
        return_value=MagicMock(status_code=200, text="<xml><child></child></xml>"),
    )


@pytest.fixture()
def empty_response(mocker):
    response = mocker.MagicMock(status_code=200, text="<xml><child></child></xml>")
    return response


@pytest.fixture()
def patched_http_call(mocker):
    """This will stop any http calls inside any test."""
    return mocker.patch(
        "plexapi.server.requests.sessions.Session.send",
        return_value=MagicMock(status_code=200, text="<xml><child></child></xml>"),
    )


# ---------------------------------
#  Utility Functions
# ---------------------------------
def is_datetime(value):
    if value is None:
        return True
    return value > MIN_DATETIME


def is_int(value, gte=1):
    return int(value) >= gte


def is_float(value, gte=1.0):
    return float(value) >= gte


def is_bool(value):
    return value is True or value is False


def is_metadata(key, prefix="/library/metadata/", contains="", suffix=""):
    try:
        assert key.startswith(prefix)
        assert contains in key
        assert key.endswith(suffix)
        return True
    except AssertionError:
        return False


def is_part(key):
    return is_metadata(key, prefix="/library/parts/")


def is_section(key):
    return is_metadata(key, prefix="/library/sections/")


def is_string(value, gte=1):
    return isinstance(value, str) and len(value) >= gte


def is_art(key):
    return is_metadata(key, contains="/art/")


def is_banner(key):
    return is_metadata(key, contains="/banner/")


def is_thumb(key):
    return is_metadata(key, contains="/thumb/")


def is_composite(key, prefix="/library/metadata/"):
    return is_metadata(key, prefix=prefix, contains="/composite/")


def wait_until(condition_function, delay=0.25, timeout=1, *args, **kwargs):
    start = time.time()
    ready = condition_function(*args, **kwargs)
    retries = 1
    while not ready and time.time() - start < timeout:
        retries += 1
        time.sleep(delay)
        ready = condition_function(*args, **kwargs)

    assert ready, f"Wait timeout after {int(retries)} retries, {time.time() - start:.2f} seconds"

    return ready


def detect_color_image(file, thumb_size=150, MSE_cutoff=22, adjust_color_bias=True):
    # http://stackoverflow.com/questions/20068945/detect-if-image-is-color-grayscale-or-black-and-white-with-python-pil
    pilimg = Image.open(file)
    bands = pilimg.getbands()
    if bands == ("R", "G", "B") or bands == ("R", "G", "B", "A"):
        thumb = pilimg.resize((thumb_size, thumb_size))
        sse, bias = 0, [0, 0, 0]
        if adjust_color_bias:
            bias = ImageStat.Stat(thumb).mean[:3]
            bias = [b - sum(bias) / 3 for b in bias]
        for pixel in thumb.getdata():
            mu = sum(pixel) / 3
            sse += sum(
                (pixel[i] - mu - bias[i]) * (pixel[i] - mu - bias[i]) for i in [0, 1, 2]
            )
        mse = float(sse) / (thumb_size * thumb_size)
        return "grayscale" if mse <= MSE_cutoff else "color"
    elif len(bands) == 1:
        return "blackandwhite"


def detect_dominant_hexcolor(file):
    # https://stackoverflow.com/questions/3241929/python-find-dominant-most-common-color-in-an-image
    pilimg = Image.open(file)
    pilimg.convert("RGB")
    pilimg.resize((1, 1), resample=0)
    rgb_color = pilimg.getpixel((0, 0))
    return "{:02x}{:02x}{:02x}".format(*rgb_color)


def detect_color_distance(hex1, hex2, threshold=100):
    rgb1 = ImageColor.getcolor("#" + hex1, "RGB")
    rgb2 = ImageColor.getcolor("#" + hex2, "RGB")
    return math.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(rgb1, rgb2))) <= threshold
