# -*- coding: utf-8 -*-
from datetime import datetime

import pytest
from plexapi.exceptions import BadRequest, NotFound

from . import conftest as utils

TEST_MIXIN_FIELD = "Test Field"
TEST_MIXIN_DATE = utils.MIN_DATETIME
TEST_MIXIN_TAG = "Test Tag !@#$%^&*()-_=+[];:'\"/?,."
CUTE_CAT_SHA1 = "9f7003fc401761d8e0b0364d428b2dab2f789dbb"
AUDIO_STUB_SHA1 = "1abc20d5fdc904201bf8988ca6ef30f96bb73617"


def _test_mixins_field(obj, attr, field_method):
    edit_field_method = getattr(obj, "edit" + field_method)
    _value = lambda: getattr(obj, attr)
    _fields = lambda: [f for f in obj.fields if f.name == attr]

    # Check field does not match to begin with
    default_value = _value()
    if isinstance(default_value, datetime):
        test_value = TEST_MIXIN_DATE
    elif isinstance(default_value, int):
        test_value = default_value + 1
    else:
        test_value = TEST_MIXIN_FIELD
    assert default_value != test_value

    # Edit and lock the field
    edit_field_method(test_value)
    obj.reload()
    value = _value()
    fields = _fields()
    assert value == test_value
    assert fields and fields[0].locked

    # Reset and unlock the field to restore the clean state
    edit_field_method(default_value, locked=False)
    obj.reload()
    value = _value()
    fields = _fields()
    assert value == default_value
    assert not fields


def edit_added_at(obj):
    _test_mixins_field(obj, "addedAt", "AddedAt")


def edit_content_rating(obj):
    _test_mixins_field(obj, "contentRating", "ContentRating")


def edit_edition_title(obj):
    _test_mixins_field(obj, "editionTitle", "EditionTitle")


def edit_originally_available(obj):
    _test_mixins_field(obj, "originallyAvailableAt", "OriginallyAvailable")


def edit_original_title(obj):
    _test_mixins_field(obj, "originalTitle", "OriginalTitle")


def edit_sort_title(obj):
    _test_mixins_field(obj, "titleSort", "SortTitle")


def edit_studio(obj):
    _test_mixins_field(obj, "studio", "Studio")


def edit_summary(obj):
    _test_mixins_field(obj, "summary", "Summary")


def edit_tagline(obj):
    _test_mixins_field(obj, "tagline", "Tagline")


def edit_title(obj):
    _test_mixins_field(obj, "title", "Title")


def edit_track_artist(obj):
    _test_mixins_field(obj, "originalTitle", "TrackArtist")


def edit_track_number(obj):
    _test_mixins_field(obj, "index", "TrackNumber")


def edit_track_disc_number(obj):
    _test_mixins_field(obj, "parentIndex", "DiscNumber")


def edit_photo_captured_time(obj):
    _test_mixins_field(obj, "originallyAvailableAt", "CapturedTime")


def _test_mixins_tag(obj, attr, tag_method):
    add_tag_method = getattr(obj, "add" + tag_method)
    remove_tag_method = getattr(obj, "remove" + tag_method)
    field_name = obj._tagSingular(attr)
    _tags = lambda: [t.tag for t in getattr(obj, attr)]
    _fields = lambda: [f for f in obj.fields if f.name == field_name]

    # Check tag is not present to begin with
    tags = _tags()
    assert TEST_MIXIN_TAG not in tags

    # Add tag string and lock the field
    add_tag_method(TEST_MIXIN_TAG)
    obj.reload()
    tags = _tags()
    fields = _fields()
    assert TEST_MIXIN_TAG in tags
    assert fields and fields[0].locked

    # Remove MediaTag object
    mediaTag = next(t for t in getattr(obj, attr) if t.tag == TEST_MIXIN_TAG)
    remove_tag_method(mediaTag)
    obj.reload()
    tags = _tags()
    assert TEST_MIXIN_TAG not in tags

    # Add MediaTag object
    add_tag_method(mediaTag)
    obj.reload()
    tags = _tags()
    assert TEST_MIXIN_TAG in tags

    # Remove tag string and unlock to field to restore the clean state
    remove_tag_method(TEST_MIXIN_TAG, locked=False)
    obj.reload()
    tags = _tags()
    fields = _fields()
    assert TEST_MIXIN_TAG not in tags
    assert not fields


def edit_collection(obj):
    _test_mixins_tag(obj, "collections", "Collection")


def edit_country(obj):
    _test_mixins_tag(obj, "countries", "Country")


def edit_director(obj):
    _test_mixins_tag(obj, "directors", "Director")


def edit_genre(obj):
    _test_mixins_tag(obj, "genres", "Genre")


def edit_label(obj):
    _test_mixins_tag(obj, "labels", "Label")


def edit_mood(obj):
    _test_mixins_tag(obj, "moods", "Mood")


def edit_producer(obj):
    _test_mixins_tag(obj, "producers", "Producer")


def edit_similar_artist(obj):
    _test_mixins_tag(obj, "similar", "SimilarArtist")


def edit_style(obj):
    _test_mixins_tag(obj, "styles", "Style")


def edit_tag(obj):
    _test_mixins_tag(obj, "tags", "Tag")


def edit_writer(obj):
    _test_mixins_tag(obj, "writers", "Writer")


def _test_mixins_lock_image(obj, attr):
    cap_attr = attr[:-1].capitalize()
    lock_img_method = getattr(obj, "lock" + cap_attr)
    unlock_img_method = getattr(obj, "unlock" + cap_attr)
    field = "thumb" if attr == 'posters' else attr[:-1]
    _fields = lambda: [f.name for f in obj.fields]
    assert field not in _fields()
    lock_img_method()
    obj.reload()
    assert field in _fields()
    unlock_img_method()
    obj.reload()
    assert field not in _fields()


def lock_art(obj):
    _test_mixins_lock_image(obj, "arts")


def lock_banner(obj):
    _test_mixins_lock_image(obj, "banners")


def lock_poster(obj):
    _test_mixins_lock_image(obj, "posters")


def _test_mixins_edit_image(obj, attr):
    cap_attr = attr[:-1].capitalize()
    get_img_method = getattr(obj, attr)
    set_img_method = getattr(obj, "set" + cap_attr)
    upload_img_method = getattr(obj, "upload" + cap_attr)
    images = get_img_method()
    if images:
        default_image = images[0]
        image = images[0]
        assert len(image.key) >= 10
        if not image.ratingKey.startswith(("default://", "id://", "media://", "upload://")):
            assert image.provider
        assert len(image.ratingKey) >= 10
        assert utils.is_bool(image.selected)
        assert len(image.thumb) >= 10
        if len(images) >= 2:
            # Select a different image
            set_img_method(images[1])
            images = get_img_method()
            assert images[0].selected is False
            assert images[1].selected is True
    else:
        default_image = None

    # Test upload image from file
    upload_img_method(filepath=utils.STUB_IMAGE_PATH)
    images = get_img_method()
    file_image = [
        i for i in images
        if i.ratingKey.startswith("upload://") and i.ratingKey.endswith(CUTE_CAT_SHA1)
    ]
    assert file_image

    # Reset to default image
    if default_image:
        set_img_method(default_image)

    # Test upload image from file-like ojbect
    with open(utils.STUB_IMAGE_PATH, "rb") as f:
        upload_img_method(filepath=f)
        images = get_img_method()
        file_image = [
            i for i in images
            if i.ratingKey.startswith("upload://") and i.ratingKey.endswith(CUTE_CAT_SHA1)
        ]
        assert file_image

    # Reset to default image
    if default_image:
        set_img_method(default_image)

    # Unlock the image
    unlock_img_method = getattr(obj, "unlock" + cap_attr)
    unlock_img_method()


def edit_art(obj):
    _test_mixins_edit_image(obj, "arts")


def edit_banner(obj):
    _test_mixins_edit_image(obj, "banners")


def edit_poster(obj):
    _test_mixins_edit_image(obj, "posters")


def _test_mixins_imageUrl(obj, attr):
    url = getattr(obj, attr + "Url")
    if getattr(obj, attr):
        assert url.startswith(utils.SERVER_BASEURL)
        assert "/library/metadata/" in url or "/library/collections/" in url
        assert attr in url or "composite" in url
        if attr == "thumb":
            assert getattr(obj, "posterUrl") == url
    else:
        assert url is None


def attr_artUrl(obj):
    _test_mixins_imageUrl(obj, "art")


def attr_bannerUrl(obj):
    _test_mixins_imageUrl(obj, "banner")


def attr_posterUrl(obj):
    _test_mixins_imageUrl(obj, "thumb")


def _test_mixins_edit_theme(obj):
    _fields = lambda: [f.name for f in obj.fields]

    # Test upload theme from file
    obj.uploadTheme(filepath=utils.STUB_MP3_PATH)
    themes = obj.themes()
    file_theme = [
        t for t in themes
        if t.ratingKey.startswith("upload://") and t.ratingKey.endswith(AUDIO_STUB_SHA1)
    ]
    assert file_theme
    obj.reload()
    assert "theme" in _fields()

    # Unlock the theme
    obj.unlockTheme()
    obj.reload()
    assert "theme" not in _fields()
    
    # Lock the theme
    obj.lockTheme()
    obj.reload()
    assert "theme" in _fields()
    with pytest.raises(NotImplementedError):
        obj.setTheme(themes[0])


def edit_theme(obj):
    _test_mixins_edit_theme(obj)


def _test_mixins_themeUrl(obj):
    url = obj.themeUrl
    if url:
        assert url.startswith(utils.SERVER_BASEURL)
        assert "/library/metadata/" in url
        assert "theme" in url
    else:
        assert url is None


def attr_themeUrl(obj):
    _test_mixins_themeUrl(obj)


def _test_mixins_editAdvanced(obj):
    for pref in obj.preferences():
        currentPref = obj.preference(pref.id)
        currentValue = currentPref.value
        newValue = next(v for v in pref.enumValues if v != currentValue)
        obj.editAdvanced(**{pref.id: newValue})
        obj.reload()
        newPref = obj.preference(pref.id)
        assert newPref.value == newValue


def _test_mixins_editAdvanced_bad_pref(obj):
    with pytest.raises(NotFound):
        assert obj.preference("bad-pref")


def _test_mixins_defaultAdvanced(obj):
    obj.defaultAdvanced()
    obj.reload()
    for pref in obj.preferences():
        assert pref.value == pref.default


def edit_advanced_settings(obj):
    _test_mixins_editAdvanced(obj)
    _test_mixins_editAdvanced_bad_pref(obj)
    _test_mixins_defaultAdvanced(obj)


def edit_rating(obj):
    obj.rate(10.0)
    obj.reload()
    assert utils.is_datetime(obj.lastRatedAt)
    assert obj.userRating == 10.0
    obj.rate()
    obj.reload()
    assert obj.userRating is None
    with pytest.raises(BadRequest):
        assert obj.rate("bad-rating")
    with pytest.raises(BadRequest):
        assert obj.rate(-1)
    with pytest.raises(BadRequest):
        assert obj.rate(100)
