#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plex-ListSettings is used during development of PlexAPI and loops through available
setting items and separates them by group as well as display the variable type. The
resulting list is used for the creation of docs/settingslist.rst.
"""
from collections import defaultdict
from os.path import abspath, dirname, join
from plexapi import utils
from plexapi.server import PlexServer

GROUPNAMES = {'butler':'Scheduled Task', 'dlna':'DLNA'}
OUTPUT = join(dirname(dirname(abspath(__file__))), 'docs/settingslist.rst')


def _setting_group(setting):
    if not setting.label and not setting.summary: return 'undocumented'
    if setting.group == '': return 'misc'
    return setting.group


def _write_settings(handle, groups, group):
    title = GROUPNAMES.get(group, group.title())
    print('\n%s Settings\n%s' % (title, '-' * (len(title) + 9)))
    handle.write('%s Settings\n%s\n' % (title, '-' * (len(title) + 9)))
    for setting in groups[group]:
        print('  %s (%s)' % (utils.lowerFirst(setting.id), setting.type))
        # Special case undocumented settings
        if group == 'undocumented':
            handle.write('* **%s (%s)**' % (utils.lowerFirst(setting.id), setting.type))
            if any((setting.default, setting.enumValues)):
                handle.write(': ')
                if setting.default: handle.write('default: %s' % setting.default)
                if all((setting.default, setting.enumValues)): handle.write('; ')
                if setting.enumValues: handle.write('choices: %s' % setting._data.attrib['enumValues'])
            handle.write('\n')
            continue
        # Write setting details to file
        handle.write('**%s (%s)**\n' % (utils.lowerFirst(setting.id), setting.type))
        if any((setting.label, setting.summary, setting.default, setting.enumValues)):
            handle.write('  ')
            if setting.label: handle.write('%s.' % setting.label)
            if setting.summary: handle.write(' %s' % setting.summary)
            if any((setting.default, setting.enumValues)):
                handle.write(' (')
                if setting.default: handle.write('default: %s' % setting.default)
                if all((setting.default, setting.enumValues)): handle.write('; ')
                if setting.enumValues: handle.write('choices: %s' % setting._data.attrib['enumValues'])
                handle.write(')')
            handle.write('\n')
        handle.write('\n')
    handle.write('\n')


def list_settings():
    # Place settings into groups..
    plex = PlexServer()
    groups = defaultdict(list)
    for setting in plex.settings.all():
        group = _setting_group(setting)
        groups[group].append(setting)
    # Build the rst output file
    special_groups = ('general', 'misc', 'undocumented')
    with open(OUTPUT, 'w') as handle:
        _write_settings(handle, groups, 'general')
        for group in [g for g in sorted(groups.keys()) if g not in special_groups]:
            _write_settings(handle, groups, group)
        _write_settings(handle, groups, 'misc')
        _write_settings(handle, groups, 'undocumented')


if __name__ == '__main__':
    print(__doc__)
    list_settings()
