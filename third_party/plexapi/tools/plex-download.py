#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Allows downloading a Plex media item from a local or shared library. You
may specify the item by the PlexWeb url (everything after !) or by
manually searching the items from the command line wizard.

Original contribution by lad1337.
"""
import argparse
import os
import re
from urllib.parse import unquote

from plexapi import utils
from plexapi.video import Episode, Movie, Show

VALID_TYPES = (Movie, Episode, Show)


def search_for_item(url=None):
    if url: return get_item_from_url(opts.url)
    servers = [s for s in account.resources() if 'server' in s.provides]
    server = utils.choose('Choose a Server', servers, 'name').connect()
    query = input('What are you looking for?: ')
    item  = []
    items = [i for i in server.search(query) if i.__class__ in VALID_TYPES]
    items = utils.choose('Choose result', items, lambda x: '(%s) %s' % (x.type.title(), x.title[0:60]))

    if not isinstance(items, list):
        items = [items]

    for i in items:
        if isinstance(i, Show):
            display = lambda i: '%s %s %s' % (i.grandparentTitle, i.seasonEpisode, i.title)
            selected_eps = utils.choose('Choose episode', i.episodes(), display)
            if isinstance(selected_eps, list):
                item += selected_eps
            else:
                item.append(selected_eps)

        else:
            item.append(i)

    if not isinstance(item, list):
        item = [item]

    return item


def get_item_from_url(url):
    # Parse the ClientID and Key from the URL
    clientid = re.findall('[a-f0-9]{40}', url)
    key = re.findall('key=(.*?)(&.*)?$', url)
    if not clientid or not key:
        raise SystemExit('Cannot parse URL: %s' % url)
    clientid = clientid[0]
    key = unquote(key[0][0])
    # Connect to the server and fetch the item
    servers = [r for r in account.resources() if r.clientIdentifier == clientid]
    if len(servers) != 1:
        raise SystemExit('Unknown or ambiguous client id: %s' % clientid)
    server = servers[0].connect()
    return server.fetchItem(key)

if __name__ == '__main__':
    # Command line parser
    from plexapi import CONFIG
    from tqdm import tqdm
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-u', '--username', help='Your Plex username',
                        default=CONFIG.get('auth.myplex_username'))
    parser.add_argument('-p', '--password', help='Your Plex password',
                        default=CONFIG.get('auth.myplex_password'))
    parser.add_argument('--url', default=None, help='Download from URL (only paste after !)')
    opts = parser.parse_args()
    # Search item to download
    account = utils.getMyPlexAccount(opts)
    items = search_for_item(opts.url)
    for item in items:
        for part in item.iterParts():
            # We do this manually since we don't want to add a progress to Episode etc
            filename = '%s.%s' % (item._prettyfilename(), part.container)
            url = item._server.url('%s?download=1' % part.key)
            filepath = utils.download(url, token=item._server._token, filename=filename, savepath=os.getcwd(),
                                      session=item._server._session, showstatus=True)
            #print('  %s' % filepath)
