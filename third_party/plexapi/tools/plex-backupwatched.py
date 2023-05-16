#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backup and restore the watched status of Plex libraries to a json file.
"""
import argparse, json
from collections import defaultdict
from plexapi import utils

SECTIONS = ('movie', 'show')


def _find_server(account, servername=None):
    """ Find and return a PlexServer object. """
    servers = servers = [s for s in account.resources() if 'server' in s.provides]
    # If servername specified find and return it
    if servername is not None:
        for server in servers:
            if server.name == servername:
                return server.connect()
        raise SystemExit('Unknown server name: %s' % servername)
    # If servername not specified; allow user to choose
    return utils.choose('Choose a Server', servers, 'name').connect()


def _item_key(item):
    if item.type == 'movie':
        return '%s.%s' % (item._prettyfilename().lower(), item.year)
    elif item.type == 'episode':
        return '%s.%s' % (item._prettyfilename().lower(), item.year)


def _iter_sections(plex, opts):
    libraries = opts.libraries.split(',') if opts.libraries else []
    libraries = [l.strip().lower() for l in libraries]
    for section in plex.library.sections():
        title = section.title.lower()
        if section.type in SECTIONS and (not libraries or title in libraries):
            yield section


def _iter_items(section):
    if section.type == 'movie':
        for movie in section.all():
            yield movie
    elif section.type == 'show':
        for show in section.all():
            for episode in show.episodes():
                yield episode


def backup_watched(plex, opts):
    """ Backup watched status to the specified filepath. """
    data = defaultdict(lambda: {})
    for section in _iter_sections(plex, opts):
        print('Fetching watched status for %s..' % section.title)
        skey = section.title.lower()
        for item in _iter_items(section):
            if not opts.watchedonly or item.isWatched:
                ikey = _item_key(item)
                data[skey][ikey] = item.isWatched
                import pprint; pprint.pprint(item.__dict__); break
    print('Writing backup file to %s' % opts.filepath)
    with open(opts.filepath, 'w') as handle:
        json.dump(dict(data), handle, sort_keys=True, indent=2)


def restore_watched(plex, opts):
    """ Restore watched status from the specified filepath. """
    with open(opts.filepath, 'r') as handle:
        source = json.load(handle)
    # Find the differences
    differences = defaultdict(lambda: {})
    for section in _iter_sections(plex, opts):
        print('Finding differences in %s..' % section.title)
        skey = section.title.lower()
        for item in _iter_items(section):
            ikey = _item_key(item)
            sval = source.get(skey,{}).get(ikey)
            if sval is None:
                raise SystemExit('%s not found' % ikey)
            if (sval is not None and item.isWatched != sval) and (not opts.watchedonly or sval):
                differences[skey][ikey] = {'isWatched':sval, 'item':item}
    print('Applying %s differences to destination' % len(differences))
    import pprint; pprint.pprint(differences)


if __name__ == '__main__':
    from plexapi import CONFIG
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', help='Action to perform: backup or restore', choices=('backup', 'restore'))
    parser.add_argument('filepath', help='File path to backup to or restore from')
    parser.add_argument('-u', '--username', default=CONFIG.get('auth.myplex_username'), help='Plex username')
    parser.add_argument('-p', '--password', default=CONFIG.get('auth.myplex_password'), help='Plex password')
    parser.add_argument('-s', '--servername', help='Plex server name')
    parser.add_argument('-w', '--watchedonly', default=False, action='store_true', help='Only backup or restore watched items.')
    parser.add_argument('-l', '--libraries', help='Only backup or restore the specified libraries (comma separated).')
    opts = parser.parse_args()
    account = utils.getMyPlexAccount(opts)
    plex = _find_server(account, opts.servername)
    action = backup_watched if opts.action == 'backup' else restore_watched
    action(plex, opts)
