# -*- coding: utf-8 -*-
from urllib.parse import quote_plus

import pytest

from . import test_media, test_mixins


def test_photo_Photoalbum(photoalbum):
    assert len(photoalbum.albums()) == 3
    assert len(photoalbum.photos()) == 3
    cats_in_bed = photoalbum.album("Cats in bed")
    assert len(cats_in_bed.photos()) == 7
    a_pic = cats_in_bed.photo("photo7")
    assert a_pic


@pytest.mark.xfail(reason="Changing images fails randomly")
def test_photo_Photoalbum_mixins_images(photoalbum):
    # test_mixins.lock_art(photoalbum)  # Unlocking photoalbum artwork is broken in Plex
    # test_mixins.lock_poster(photoalbum)  # Unlocking photoalbum poster is broken in Plex
    test_mixins.edit_art(photoalbum)
    test_mixins.edit_poster(photoalbum)
    test_mixins.attr_artUrl(photoalbum)
    test_mixins.attr_posterUrl(photoalbum)


def test_photo_Photoalbum_mixins_rating(photoalbum):
    test_mixins.edit_rating(photoalbum)


def test_photo_Photoalbum_mixins_fields(photoalbum):
    test_mixins.edit_added_at(photoalbum)
    test_mixins.edit_sort_title(photoalbum)
    test_mixins.edit_summary(photoalbum)
    test_mixins.edit_title(photoalbum)


def test_photo_Photoalbum_PlexWebURL(plex, photoalbum):
    url = photoalbum.getWebURL()
    assert url.startswith('https://app.plex.tv/desktop')
    assert plex.machineIdentifier in url
    assert 'details' in url
    assert quote_plus(photoalbum.key) in url
    assert 'legacy=1' in url


def test_photo_Photo_mixins_rating(photo):
    test_mixins.edit_rating(photo)


def test_photo_Photo_mixins_fields(photo):
    test_mixins.edit_added_at(photo)
    test_mixins.edit_sort_title(photo)
    test_mixins.edit_summary(photo)
    test_mixins.edit_title(photo)
    test_mixins.edit_photo_captured_time(photo)


def test_photo_Photo_mixins_tags(photo):
    test_mixins.edit_tag(photo)


def test_photo_Photo_media_tags(photo):
    photo.reload()
    test_media.tag_tag(photo)


def test_photo_Photo_PlexWebURL(plex, photo):
    url = photo.getWebURL()
    assert url.startswith('https://app.plex.tv/desktop')
    assert plex.machineIdentifier in url
    assert 'details' in url
    assert quote_plus(photo.parentKey) in url
    assert 'legacy=1' in url


def test_photo_Photoalbum_download(monkeydownload, tmpdir, photoalbum):
    total = 0
    for album in photoalbum.albums():
        total += len(album.photos()) + len(album.clips())
    total += len(photoalbum.photos())
    total += len(photoalbum.clips())
    filepaths = photoalbum.download(savepath=str(tmpdir))
    assert len(filepaths) == total
    subfolders = photoalbum.download(savepath=str(tmpdir), subfolders=True)
    assert len(subfolders) == total


def test_photo_Photo_download(monkeydownload, tmpdir, photo):
    filepaths = photo.download(savepath=str(tmpdir))
    assert len(filepaths) == 1
