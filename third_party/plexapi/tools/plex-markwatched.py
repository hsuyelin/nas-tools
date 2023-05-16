#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plex-MarkWatched is a useful to always mark a show as watched. This comes in
handy when you have a show you keep downloaded, but do not religiously watch
every single episode that is downloaded. By marking everything watched, it
will keep the show out of your OnDeck list inside Plex.

Usage:
Intended usage is to add the tak 'markwatched' to any show you want to have
this behaviour. Then simply add this script to run on a schedule and you
should be all set.

Example Crontab:
*/5 * * * * /home/atodd/plex-markwatched.py >> /home/atodd/plex-markwatched.log 2>&1
"""
from datetime import datetime
from plexapi.server import PlexServer


def _has_markwatched_tag(item):
    collections = item.show().collections if item.type == 'episode' else item.collections
    tags = [c.tag.lower() for c in collections]
    return 'markwatched' in tags


def _get_title(item):
    if item.type == 'episode':
        return '{title} {episode}'.format(title=item.grandparentTitle, episode=item.seasonEpisode)
    return item.title


def _iter_items(search):
    for item in search:
        if item.type in ['show']:
            for episode in item.episodes():
                yield episode
            break
        yield item


if __name__ == '__main__':
    datestr = lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # noqa
    print('{datestr} Starting plex-markwatched script..'.format(datestr=datestr()))
    plex = PlexServer()
    for section in plex.library.sections():
        print('{datestr} Checking {section.title} for unwatched items..'.format(datestr=datestr()))
        for item in _iter_items(section.search(collection='markwatched')):
            if not item.isWatched:
                print('{datestr}  Marking {_get_title(item)} watched.'.format(datestr=datestr()))
                item.markWatched()
    # Check all OnDeck items
    print('{datestr} Checking OnDeck for unwatched items..'.format(datestr=datestr()))
    for item in plex.library.onDeck():
        if not item.isWatched and _has_markwatched_tag(item):
            print('{datestr}  Marking {_get_title(item)} watched.'.format(datestr=datestr()))
            item.markWatched()
