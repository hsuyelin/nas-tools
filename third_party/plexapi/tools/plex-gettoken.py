#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plex-GetToken is a simple method to retrieve a Plex account token.
"""
from plexapi.myplex import MyPlexAccount

username = input("Plex username: ")
password = input("Plex password: ")

account = MyPlexAccount(username, password)
print(account.authenticationToken)
