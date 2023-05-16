#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remove current Plex Server and a Client from MyPlex account. Useful when running tests in CI.
"""
from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
from plexapi import X_PLEX_IDENTIFIER


if __name__ == '__main__':
    myplex = MyPlexAccount()
    plex = PlexServer(token=myplex.authenticationToken)

    # Remove the test server
    for device in plex.myPlexAccount().devices():
        if device.clientIdentifier == plex.machineIdentifier:
            print('Removing device "%s", with id "%s"' % (device.name, device. clientIdentifier))
            device.delete()

    # Remove the test sync client
    sync_client_identifier = 'test-sync-client-%s' % X_PLEX_IDENTIFIER
    for device in plex.myPlexAccount().devices():
        if device.clientIdentifier == sync_client_identifier:
            print('Removing device "%s", with id "%s"' % (device.name, device. clientIdentifier))
            device.delete()
            break

    # If we suddenly remove the client first we wouldn't be able to authenticate to delete the server
    for device in plex.myPlexAccount().devices():
        if device.clientIdentifier == X_PLEX_IDENTIFIER:
            print('Removing device "%s", with id "%s"' % (device.name, device. clientIdentifier))
            device.delete()
            break
