#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Helper script to bump the current version."""
import argparse
import re
import subprocess

from packaging.version import Version

from plexapi import const

SUPPORTED_BUMP_TYPES = ["patch", "minor", "major"]


def _bump_release(release, bump_type):
    """Return a bumped release tuple consisting of 3 numbers."""
    major, minor, patch = release

    if bump_type == "patch":
        patch += 1
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "major":
        major += 1
        minor = 0
        patch = 0

    return major, minor, patch


def bump_version(version, bump_type):
    """Return a new version given a current version and action."""
    new_release = _bump_release(version.release, bump_type)
    temp = Version("0")
    temp._version = version._version._replace(release=new_release)
    return Version(str(temp))


def write_version(version):
    """Update plexapi constant file with new version."""
    with open("plexapi/const.py") as f:
        content = f.read()

    version_names = ["MAJOR", "MINOR", "PATCH"]
    version_values = str(version).split(".", 2)

    for n, v in zip(version_names, version_values):
        version_line = f"{n}_VERSION = "
        content = re.sub(f"{version_line}.*\n", f"{version_line}{v}\n", content)

    with open("plexapi/const.py", "wt") as f:
        content = f.write(content)


def main():
    """Execute script."""
    parser = argparse.ArgumentParser(description="Bump version of plexapi")
    parser.add_argument(
        "bump_type",
        help="The type of version bump to perform",
        choices=SUPPORTED_BUMP_TYPES,
    )
    parser.add_argument(
        "--commit", action="store_true", help="Create a version bump commit"
    )
    parser.add_argument(
        "--tag", action="store_true", help="Tag the commit with the release version"
    )
    arguments = parser.parse_args()

    if arguments.tag and not arguments.commit:
        parser.error("--tag requires use of --commit")

    if arguments.commit and subprocess.run(["git", "diff", "--quiet"]).returncode == 1:
        print("Cannot use --commit because git is dirty")
        return

    current = Version(const.__version__)
    bumped = bump_version(current, arguments.bump_type)
    assert bumped > current, "Bumped version is not newer than old version"

    write_version(bumped)

    if not arguments.commit:
        return

    subprocess.run(["git", "commit", "-nam", f"Release {bumped}"])

    if arguments.tag:
        subprocess.run(["git", "tag", str(bumped), "-m", f"Release {bumped}"])

def test_bump_version():
    """Make sure it all works."""
    import pytest

    assert bump_version(Version("4.7.0"), "patch") == Version("4.7.1")
    assert bump_version(Version("4.7.0"), "minor") == Version("4.8.0")
    assert bump_version(Version("4.7.3"), "minor") == Version("4.8.0")
    assert bump_version(Version("4.7.0"), "major") == Version("5.0.0")
    assert bump_version(Version("4.7.3"), "major") == Version("5.0.0")
    assert bump_version(Version("5.0.0"), "major") == Version("6.0.0")


if __name__ == "__main__":
    main()
