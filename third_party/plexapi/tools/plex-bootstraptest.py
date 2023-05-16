#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The script is used to bootstrap a the test environment for plexapi
with all the libraries required for testing.

By default this uses a docker.

It can be used manually using:
python plex-bootraptest.py --no-docker --server-name name_of_server --account Hellowlol --password yourpassword

"""
import argparse
import os
import shutil
import socket
import time
from glob import glob
from os import makedirs
from shutil import copyfile, which
from subprocess import call
from uuid import uuid4

import plexapi
from plexapi.exceptions import BadRequest, NotFound
from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
from plexapi.utils import SEARCHTYPES
from tqdm import tqdm

DOCKER_CMD = [
    "docker",
    "run",
    "-d",
    "--name",
    "plex-test-%(container_name_extra)s%(image_tag)s",
    "--restart",
    "on-failure",
    "-p",
    "32400:32400/tcp",
    "-p",
    "3005:3005/tcp",
    "-p",
    "8324:8324/tcp",
    "-p",
    "32469:32469/tcp",
    "-p",
    "1900:1900/udp",
    "-p",
    "32410:32410/udp",
    "-p",
    "32412:32412/udp",
    "-p",
    "32413:32413/udp",
    "-p",
    "32414:32414/udp",
    "-e",
    "PLEX_CLAIM=%(claim_token)s",
    "-e",
    "ADVERTISE_IP=http://%(advertise_ip)s:32400/",
    "-e",
    "TZ=%(timezone)s",
    "-e",
    "LANG=%(language)s",
    "-h",
    "%(hostname)s",
    "-v",
    "%(destination)s/db:/config",
    "-v",
    "%(destination)s/transcode:/transcode",
    "-v",
    "%(destination)s/media:/data",
    "plexinc/pms-docker:%(image_tag)s",
]


BASE_DIR_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUB_MOVIE_PATH = os.path.join(BASE_DIR_PATH, "tests", "data", "video_stub.mp4")
STUB_MP3_PATH = os.path.join(BASE_DIR_PATH, "tests", "data", "audio_stub.mp3")
STUB_IMAGE_PATH = os.path.join(BASE_DIR_PATH, "tests", "data", "cute_cat.jpg")


def check_ext(path, ext):
    """I hate glob so much."""
    result = []
    for root, dirs, fil in os.walk(path):
        for f in fil:
            fp = os.path.join(root, f)
            if fp.endswith(ext):
                result.append(fp)

    return result


class ExistingSection(Exception):
    """This server has sections, exiting"""

    def __init__(self, *args):
        raise SystemExit("This server has sections exiting")


def clean_pms(server, path):
    for section in server.library.sections():
        print("Deleting %s" % section.title)
        section.delete()

    server.library.cleanBundles()
    server.library.optimize()
    print("optimized db and removed any bundles")

    shutil.rmtree(path, ignore_errors=False, onerror=None)
    print("Deleted %s" % path)


def setup_music(music_path, docker=False):
    print("Setup files for the Music section..")
    makedirs(music_path, exist_ok=True)

    all_music = {

        "Broke for free": {
            "Layers": [
                "1 - As Colorful As Ever.mp3",
                #"02 - Knock Knock.mp3",
                #"03 - Only Knows.mp3",
                #"04 - If.mp3",
                #"05 - Note Drop.mp3",
                #"06 - Murmur.mp3",
                #"07 - Spellbound.mp3",
                #"08 - The Collector.mp3",
                #"09 - Quit Bitching.mp3",
                #"10 - A Year.mp3",
            ]
        },

    }

    m3u_file = open(os.path.join(music_path, "playlist.m3u"), "w")

    for artist, album in all_music.items():
        for k, v in album.items():
            artist_album = os.path.join(music_path, artist, k)
            makedirs(artist_album, exist_ok=True)
            for song in v:
                trackpath = os.path.join(artist_album, song)
                copyfile(STUB_MP3_PATH, trackpath)

                if docker:
                    reltrackpath = os.path.relpath(trackpath, os.path.dirname(music_path))
                    m3u_file.write(os.path.join("/data", reltrackpath) + "\n")
                else:
                    m3u_file.write(trackpath + "\n")

    m3u_file.close()

    return len(check_ext(music_path, (".mp3")))


def setup_movies(movies_path):
    print("Setup files for the Movies section..")
    makedirs(movies_path, exist_ok=True)
    if len(glob(movies_path + "/*.mkv", recursive=True)) == 4:
        return 4

    required_movies = {
        "Elephants Dream": 2006,
        "Sita Sings the Blues": 2008,
        "Big Buck Bunny": 2008,
        "Sintel": 2010,
    }
    expected_media_count = 0
    for name, year in required_movies.items():
        expected_media_count += 1
        if not os.path.isfile(get_movie_path(movies_path, name, year)):
            copyfile(STUB_MOVIE_PATH, get_movie_path(movies_path, name, year))

    return expected_media_count


def setup_images(photos_path):
    print("Setup files for the Photos section..")

    makedirs(photos_path, exist_ok=True)
    # expected_photo_count = 0
    folders = {
        ("Cats",): 3,
        ("Cats", "Cats in bed"): 7,
        ("Cats", "Cats not in bed"): 1,
        ("Cats", "Not cats in bed"): 1,
    }
    has_photos = 0
    for folder_path, required_cnt in folders.items():
        folder_path = os.path.join(photos_path, *folder_path)
        makedirs(folder_path, exist_ok=True)
        photos_in_folder = len(glob(os.path.join(folder_path, "/*.jpg")))
        while photos_in_folder < required_cnt:
            # Dunno why this is need got permission error on photo0.jpg
            photos_in_folder += 1
            full_path = os.path.join(folder_path, "photo%d.jpg" % photos_in_folder)
            copyfile(STUB_IMAGE_PATH, full_path)
            has_photos += photos_in_folder

    return len(check_ext(photos_path, (".jpg")))


def setup_show(tvshows_path):
    print("Setup files for the TV-Shows section..")
    makedirs(tvshows_path, exist_ok=True)
    makedirs(os.path.join(tvshows_path, "Game of Thrones"), exist_ok=True)
    makedirs(os.path.join(tvshows_path, "The 100"), exist_ok=True)
    required_tv_shows = {
        "Game of Thrones": [list(range(1, 11)), list(range(1, 11))],
        "The 100": [list(range(1, 14)), list(range(1, 17))],
    }
    expected_media_count = 0
    for show_name, seasons in required_tv_shows.items():
        for season_id, episodes in enumerate(seasons, start=1):
            for episode_id in episodes:
                expected_media_count += 1
                episode_path = get_tvshow_path(
                    tvshows_path, show_name, season_id, episode_id
                )
                if not os.path.isfile(episode_path):
                    copyfile(STUB_MOVIE_PATH, episode_path)

    return expected_media_count


def get_default_ip():
    """ Return the first IP address of the current machine if available. """
    available_ips = list(
        set(
            [
                i[4][0]
                for i in socket.getaddrinfo(socket.gethostname(), None)
                if i[4][0] not in ("127.0.0.1", "::1")
                and not i[4][0].startswith("fe80:")
            ]
        )
    )
    return available_ips[0] if len(available_ips) else None


def get_plex_account(opts):
    """ Authenticate with Plex using the command line options. """
    if not opts.unclaimed:
        if opts.token:
            return MyPlexAccount(token=opts.token)
        return plexapi.utils.getMyPlexAccount(opts)
    return None


def get_movie_path(movies_path, name, year):
    """ Return a movie path given its title and year. """
    return os.path.join(movies_path, "%s (%d).mp4" % (name, year))


def get_tvshow_path(tvshows_path, name, season, episode):
    """ Return a TV show path given its title, season, and episode. """
    return os.path.join(tvshows_path, name, "S%02dE%02d.mp4" % (season, episode))


def add_library_section(server, section):
    """ Add the specified section to our Plex instance. This tends to be a bit
        flaky, so we retry a few times here.
    """
    start = time.time()
    runtime = 0
    while runtime < 60:
        try:
            server.library.add(**section)
            return True
        except BadRequest as err:
            if "server is still starting up. Please retry later" in str(err):
                time.sleep(1)
                continue
            raise
        runtime = time.time() - start
    raise SystemExit("Timeout adding section to Plex instance.")


def create_section(server, section, opts):
    processed_media = 0
    expected_media_count = section.pop("expected_media_count", 0)
    expected_media_type = (section["type"],)
    if section["type"] == "show":
        expected_media_type = ("show", "season", "episode")
    if section["type"] == "artist":
        expected_media_type = ("artist", "album", "track")
    expected_media_type = tuple(SEARCHTYPES[t] for t in expected_media_type)

    def alert_callback(data):
        """ Listen to the Plex notifier to determine when metadata scanning is complete. """
        global processed_media
        if data["type"] == "timeline":
            for entry in data["TimelineEntry"]:
                if (
                    entry.get("identifier", "com.plexapp.plugins.library")
                    == "com.plexapp.plugins.library"
                ):
                    # Missed mediaState means that media was processed (analyzed & thumbnailed)
                    if (
                        "mediaState" not in entry
                        and entry["type"] in expected_media_type
                    ):
                        # state=5 means record processed, applicable only when metadata source was set
                        if entry["state"] == 5:
                            cnt = 1
                            if entry["type"] == SEARCHTYPES["show"]:
                                show = server.library.sectionByID(
                                    entry["sectionID"]
                                ).get(entry["title"])
                                cnt = show.leafCount
                            bar.update(cnt)
                            processed_media += cnt
                        # state=1 means record processed, when no metadata source was set
                        elif (
                            entry["state"] == 1
                            and entry["type"] == SEARCHTYPES["photo"]
                        ):
                            bar.update()
                            processed_media += 1

    runtime = 0
    start = time.time()
    bar = tqdm(desc="Scanning section " + section["name"], total=expected_media_count)
    notifier = server.startAlertListener(alert_callback)
    time.sleep(3)
    add_library_section(server, section)
    while bar.n < bar.total:
        if runtime >= 120:
            print("Metadata scan taking too long, but will continue anyway..")
            break
        time.sleep(3)
        runtime = int(time.time() - start)
    bar.close()
    notifier.stop()


if __name__ == "__main__":
    default_ip = get_default_ip()
    parser = argparse.ArgumentParser(description=__doc__)
    # Authentication arguments
    mg = parser.add_mutually_exclusive_group()
    g = mg.add_argument_group()
    g.add_argument("--username", help="Your Plex username")
    g.add_argument("--password", help="Your Plex password")
    mg.add_argument(
        "--token",
        help="Plex.tv authentication token",
        default=plexapi.CONFIG.get("auth.server_token"),
    )
    mg.add_argument(
        "--unclaimed",
        help="Do not claim the server",
        default=False,
        action="store_true",
    )
    # Test environment arguments
    parser.add_argument(
        "--no-docker", help="Use docker", default=False, action="store_true"
    )
    parser.add_argument(
        "--timezone", help="Timezone to set inside plex", default="UTC"
    )  # noqa
    parser.add_argument(
        "--language", help="Language to set inside plex", default="en_US.UTF-8"
    )  # noqa
    parser.add_argument(
        "--destination",
        help="Local path where to store all the media",
        default=os.path.join(os.getcwd(), "plex"),
    )  # noqa
    parser.add_argument(
        "--advertise-ip",
        help="IP address which should be advertised by new Plex instance",
        required=default_ip is None,
        default=default_ip,
    )  # noqa
    parser.add_argument(
        "--docker-tag", help="Docker image tag to install", default="latest"
    )  # noqa
    parser.add_argument(
        "--bootstrap-timeout",
        help="Timeout for each step of bootstrap, in seconds (default: %(default)s)",
        default=180,
        type=int,
    )  # noqa
    parser.add_argument(
        "--server-name",
        help="Name for the new server",
        default="plex-test-docker-%s" % str(uuid4()),
    )  # noqa
    parser.add_argument(
        "--accept-eula", help="Accept Plex's EULA", default=False, action="store_true"
    )  # noqa
    parser.add_argument(
        "--without-movies",
        help="Do not create Movies section",
        default=True,
        dest="with_movies",
        action="store_false",
    )  # noqa
    parser.add_argument(
        "--without-shows",
        help="Do not create TV Shows section",
        default=True,
        dest="with_shows",
        action="store_false",
    )  # noqa
    parser.add_argument(
        "--without-music",
        help="Do not create Music section",
        default=True,
        dest="with_music",
        action="store_false",
    )  # noqa
    parser.add_argument(
        "--without-photos",
        help="Do not create Photos section",
        default=True,
        dest="with_photos",
        action="store_false",
    )  # noqa
    parser.add_argument(
        "--show-token",
        help="Display access token after bootstrap",
        default=False,
        action="store_true",
    )  # noqa
    opts, _ = parser.parse_known_args()

    account = get_plex_account(opts)
    path = os.path.realpath(os.path.expanduser(opts.destination))
    media_path = os.path.join(path, "media")
    makedirs(media_path, exist_ok=True)

    # Download the Plex Docker image
    if opts.no_docker is False:
        print(
            "Creating Plex instance named %s with advertised ip %s"
            % (opts.server_name, opts.advertise_ip)
        )
        if which("docker") is None:
            print("Docker is required to be available")
            exit(1)
        if call(["docker", "pull", "plexinc/pms-docker:%s" % opts.docker_tag]) != 0:
            print("Got an error when executing docker pull!")
            exit(1)

        # Start the Plex Docker container

        arg_bindings = {
            "destination": path,
            "hostname": opts.server_name,
            "claim_token": account.claimToken() if account else "",
            "timezone": opts.timezone,
            "language": opts.language,
            "advertise_ip": opts.advertise_ip,
            "image_tag": opts.docker_tag,
            "container_name_extra": "" if account else "unclaimed-",
        }
        docker_cmd = [c % arg_bindings for c in DOCKER_CMD]
        exit_code = call(docker_cmd)
        if exit_code != 0:
            raise SystemExit(
                "Error %s while starting the Plex docker container" % exit_code
            )

    # Wait for the Plex container to start
    print("Waiting for the Plex to start..")
    start = time.time()
    runtime = 0
    server = None
    while not server and (runtime < opts.bootstrap_timeout):
        try:
            if account:
                server = account.device(opts.server_name).connect()
            else:
                server = PlexServer("http://%s:32400" % opts.advertise_ip)

        except KeyboardInterrupt:
            break

        except Exception as err:
            print(err)
            time.sleep(1)

        runtime = time.time() - start

    if not server:
        raise SystemExit(
            "Server didn't appear in your account after %ss" % opts.bootstrap_timeout
        )

    print("Plex container started after %ss" % int(runtime))
    print("Plex server version %s" % server.version)

    if opts.accept_eula:
        server.settings.get("acceptedEULA").set(True)
    # Disable settings for background tasks when using the test server.
    # These tasks won't work on the test server since we are using fake media files
    if not opts.unclaimed and account and account.subscriptionActive:
        server.settings.get("GenerateIntroMarkerBehavior").set("never")
        server.settings.get("GenerateCreditsMarkerBehavior").set("never")
    server.settings.get("GenerateBIFBehavior").set("never")
    server.settings.get("GenerateChapterThumbBehavior").set("never")
    server.settings.get("LoudnessAnalysisBehavior").set("never")
    server.settings.save()

    sections = []

    # Lets add a check here do somebody don't mess up
    # there normal server if they run manual tests.
    # Like i did....
    if len(server.library.sections()) and opts.no_docker is True:
        ans = input(
            "The server has %s sections, do you wish to remove it?\n> "
            % len(server.library.sections())
        )
        if ans in ("y", "Y", "Yes"):
            ans = input(
                "Are you really sure you want to delete %s libraries? There is no way back\n> "
                % len(server.library.sections())
            )
            if ans in ("y", "Y", "Yes"):
                clean_pms(server, path)
            else:
                raise ExistingSection()
        else:
            raise ExistingSection()

    # Prepare Movies section
    if opts.with_movies:
        movies_path = os.path.join(media_path, "Movies")
        num_movies = setup_movies(movies_path)
        sections.append(
            dict(
                name="Movies",
                type="movie",
                location="/data/Movies" if opts.no_docker is False else movies_path,
                agent="tv.plex.agents.movie",
                scanner="Plex Movie",
                language="en-US",
                expected_media_count=num_movies,
            )
        )

    # Prepare TV Show section
    if opts.with_shows:
        tvshows_path = os.path.join(media_path, "TV-Shows")
        num_ep = setup_show(tvshows_path)

        sections.append(
            dict(
                name="TV Shows",
                type="show",
                location="/data/TV-Shows" if opts.no_docker is False else tvshows_path,
                agent="tv.plex.agents.series",
                scanner="Plex TV Series",
                language="en-US",
                expected_media_count=num_ep,
            )
        )

    # Prepare Music section
    if opts.with_music:
        music_path = os.path.join(media_path, "Music")
        song_c = setup_music(music_path, docker=not opts.no_docker)

        sections.append(
            dict(
                name="Music",
                type="artist",
                location="/data/Music" if opts.no_docker is False else music_path,
                agent="tv.plex.agents.music",
                scanner="Plex Music",
                expected_media_count=song_c,
            )
        )

    # Prepare Photos section
    if opts.with_photos:
        photos_path = os.path.join(media_path, "Photos")
        has_photos = setup_images(photos_path)

        sections.append(
            dict(
                name="Photos",
                type="photo",
                location="/data/Photos" if opts.no_docker is False else photos_path,
                agent="com.plexapp.agents.none",
                scanner="Plex Photo Scanner",
                expected_media_count=has_photos,
            )
        )

    # Create the Plex library in our instance
    if sections:
        print("Creating the Plex libraries on %s" % server.friendlyName)
        for section in sections:
            create_section(server, section, opts)

    # Share this instance with the specified username
    if account:
        shared_username = os.environ.get("SHARED_USERNAME", "PKKid")
        try:
            user = account.user(shared_username)
            account.updateFriend(user, server)
            print("The server was shared with user %s" % shared_username)
        except NotFound:
            pass

    # Finished: Display our Plex details
    print("Base URL is %s" % server.url("", False))
    if account and opts.show_token:
        print("Auth token is %s" % account.authenticationToken)
    print("Server %s is ready to use!" % opts.server_name)
