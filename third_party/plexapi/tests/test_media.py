# -*- coding: utf-8 -*-

def _test_media_tag(obj, attr):
    tags = getattr(obj, attr)
    if tags:
        assert obj in tags[0].items()


def tag_collection(obj):
    _test_media_tag(obj, "collections")


def tag_country(obj):
    _test_media_tag(obj, "countries")


def tag_director(obj):
    _test_media_tag(obj, "directors")


def tag_genre(obj):
    _test_media_tag(obj, "genres")


def tag_label(obj):
    _test_media_tag(obj, "labels")


def tag_mood(obj):
    _test_media_tag(obj, "moods")


def tag_producer(obj):
    _test_media_tag(obj, "producers")


def tag_role(obj):
    _test_media_tag(obj, "roles")


def tag_similar(obj):
    _test_media_tag(obj, "similar")


def tag_style(obj):
    _test_media_tag(obj, "styles")


def tag_tag(obj):
    _test_media_tag(obj, "tags")


def tag_writer(obj):
    _test_media_tag(obj, "writers")
