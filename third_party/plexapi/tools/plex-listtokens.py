#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plex-ListTokens is a simple utility to fetch and list all known Plex
Server tokens your plex.tv account has access to. Because this information
comes from the plex.tv website, we need to ask for your username
and password. Alternatively, if you do not wish to enter your login
information below, you can retrieve the same information from plex.tv
at the URL: https://plex.tv/api/resources?includeHttps=1
"""
import argparse
from plexapi import utils
from plexapi.exceptions import BadRequest
from plexapi.myplex import _connect
from plexapi.server import PlexServer

SERVER = 'Plex Media Server'
FORMAT = '%-8s  %-6s  %-17s  %-25s  %-20s  %s (%s)'


def _list_resources(account, servers):
    items = []
    print('Finding Plex resources..')
    resources = account.resources()
    for r in [r for r in resources if r.accessToken]:
        for connection in r.connections:
            local = 'Local' if connection.local else 'Remote'
            extras = [r.provides]
            items.append(FORMAT % ('Resource', local, r.product, r.name, r.accessToken, connection.uri, ','.join(extras)))
            items.append(FORMAT % ('Resource', local, r.product, r.name, r.accessToken, connection.httpuri, ','.join(extras)))
            servers[connection.httpuri] = r.accessToken
            servers[connection.uri] = r.accessToken
    return items


def _list_devices(account, servers):
    items = []
    print('Finding Plex devices..')
    for d in [d for d in account.devices() if d.token]:
        for connection in d.connections:
            extras = [d.provides]
            items.append(FORMAT % ('Device', '--', d.product, d.name, d.token, connection, ','.join(extras)))
            servers[connection] = d.token
    return items


def _test_servers(servers):
    items, seen = [], set()
    print('Finding Plex clients..')
    listargs = [[PlexServer, s, t, 5] for s,t in servers.items()]
    results = utils.threaded(_connect, listargs)
    for url, token, plex, runtime in results:
        clients = plex.clients() if plex else []
        if plex and clients:
            for c in plex.clients():
                if c._baseurl not in seen:
                    extras = [plex.friendlyName] + c.protocolCapabilities
                    items.append(FORMAT % ('Client', '--', c.product, c.title, token, c._baseurl, ','.join(extras)))
                    seen.add(c._baseurl)
    return items


def _print_items(items, _filter=None):
    if _filter:
        print('Displaying items matching filter: %s' % _filter)
    print()
    for item in items:
        filtered_out = False
        for f in _filter.split():
            if f.lower() not in item.lower():
                filtered_out = True
        if not filtered_out:
            print(item)
    print()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--username', help='Your Plex username')
    parser.add_argument('--password', help='Your Plex password')
    parser.add_argument('--filter', default='', help='Only display items containing specified filter')
    opts = parser.parse_args()
    try:
        servers = {}
        account = utils.getMyPlexAccount(opts)
        items = _list_resources(account, servers)
        items += _list_devices(account, servers)
        items += _test_servers(servers)
        _print_items(items, opts.filter)
    except BadRequest as err:
        print('Unable to login to plex.tv: %s' % err)
