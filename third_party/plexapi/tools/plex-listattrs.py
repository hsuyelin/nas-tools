#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plex-ListAttrs is used during development of PlexAPI and loops through all media
items to build a collection of attributes on each media type. The resulting list
can be compared with the current object implementation in python-plexapi to track
new attributes and deprecate old ones.
"""
import argparse, copy, pickle, plexapi, os, re, sys, time
from os.path import abspath, dirname, join
from collections import defaultdict
from datetime import datetime
from plexapi import library
from plexapi.base import PlexObject
from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
from plexapi.playqueue import PlayQueue

CACHEPATH = join(dirname(abspath(__file__)), 'findattrs.pickle')
NAMESPACE = {
    'xml': defaultdict(int),
    'obj': defaultdict(int),
    'docs': defaultdict(int),
    'examples': defaultdict(set),
    'categories': defaultdict(set),
    'total': 0,
    'old': 0,
    'new': 0,
    'doc': 0,
}
IGNORES = {
    'server.PlexServer': ['baseurl', 'token', 'session'],
    'myplex.ResourceConnection': ['httpuri'],
    'client.PlexClient': ['baseurl'],
}
DONT_RELOAD = (
    'library.MovieSection',
    'library.MusicSection',
    'library.PhotoSection',
    'library.ShowSection',
    'media.MediaPart',      # tries to download the file
    'media.VideoStream',
    'media.AudioStream',
    'media.SubtitleStream',
    'myplex.MyPlexAccount',
    'myplex.MyPlexUser',
    'myplex.MyPlexResource',
    'myplex.ResourceConnection',
    'myplex.MyPlexDevice',
    'photo.Photoalbum',
    'server.Account',
    'client.PlexClient',  # we don't have the token to reload.
)
TAGATTRS = {
    'Media': 'media',
    'Country': 'countries',
}
STOP_RECURSING_AT = (
    # 'media.MediaPart',
)


class PlexAttributes():

    def __init__(self, opts):
        self.opts = opts                                            # command line options
        self.clsnames = [c for c in opts.clsnames.split(',') if c]  # list of clsnames to report (blank=all)
        self.account = MyPlexAccount()                              # MyPlexAccount instance
        self.plex = PlexServer()                                    # PlexServer instance
        self.total = 0                                              # Total objects parsed
        self.attrs = defaultdict(dict)                              # Attrs result set

    def run(self):
        starttime = time.time()
        self._parse_myplex()
        self._parse_server()
        self._parse_search()
        self._parse_library()
        self._parse_audio()
        self._parse_photo()
        self._parse_movie()
        self._parse_show()
        self._parse_client()
        self._parse_playlist()
        self._parse_sync()
        self.runtime = round((time.time() - starttime) / 60.0, 1)
        return self

    def _parse_myplex(self):
        self._load_attrs(self.account, 'myplex')
        self._load_attrs(self.account.devices(), 'myplex')
        for resource in self.account.resources():
            self._load_attrs(resource, 'myplex')
            self._load_attrs(resource.connections, 'myplex')
        self._load_attrs(self.account.users(), 'myplex')

    def _parse_server(self):
        self._load_attrs(self.plex, 'serv')
        self._load_attrs(self.plex.account(), 'serv')
        self._load_attrs(self.plex.history()[:50], 'hist')
        self._load_attrs(self.plex.history()[50:], 'hist')
        self._load_attrs(self.plex.sessions(), 'sess')

    def _parse_search(self):
        for search in ('cre', 'ani', 'mik', 'she', 'bea'):
            self._load_attrs(self.plex.search(search), 'hub')

    def _parse_library(self):
        cat = 'lib'
        self._load_attrs(self.plex.library, cat)
        # self._load_attrs(self.plex.library.all()[:50], 'all')
        self._load_attrs(self.plex.library.onDeck()[:50], 'deck')
        self._load_attrs(self.plex.library.recentlyAdded()[:50], 'add')
        for search in ('cat', 'dog', 'rat', 'gir', 'mou'):
            self._load_attrs(self.plex.library.search(search)[:50], 'srch')
        # TODO: Implement section search (remove library search?)
        # TODO: Implement section search filters

    def _parse_audio(self):
        cat = 'lib'
        for musicsection in self.plex.library.sections():
            if musicsection.TYPE == library.MusicSection.TYPE:
                self._load_attrs(musicsection, cat)
                for artist in musicsection.all():
                    self._load_attrs(artist, cat)
                    for album in artist.albums():
                        self._load_attrs(album, cat)
                        for track in album.tracks():
                            self._load_attrs(track, cat)

    def _parse_photo(self):
        cat = 'lib'
        for photosection in self.plex.library.sections():
            if photosection.TYPE == library.PhotoSection.TYPE:
                self._load_attrs(photosection, cat)
                for photoalbum in photosection.all():
                    self._load_attrs(photoalbum, cat)
                    for photo in photoalbum.photos():
                        self._load_attrs(photo, cat)

    def _parse_movie(self):
        cat = 'lib'
        for moviesection in self.plex.library.sections():
            if moviesection.TYPE == library.MovieSection.TYPE:
                self._load_attrs(moviesection, cat)
                for movie in moviesection.all():
                    self._load_attrs(movie, cat)

    def _parse_show(self):
        cat = 'lib'
        for showsection in self.plex.library.sections():
            if showsection.TYPE == library.ShowSection.TYPE:
                self._load_attrs(showsection, cat)
                for show in showsection.all():
                    self._load_attrs(show, cat)
                    for season in show.seasons():
                        self._load_attrs(season, cat)
                        for episode in season.episodes():
                            self._load_attrs(episode, cat)

    def _parse_client(self):
        for device in self.account.devices():
            client = self._safe_connect(device)
            if client is not None:
                self._load_attrs(client, 'myplex')
        for client in self.plex.clients():
            self._safe_connect(client)
            self._load_attrs(client, 'client')

    def _parse_playlist(self):
        for playlist in self.plex.playlists():
            self._load_attrs(playlist, 'pl')
            for item in playlist.items():
                self._load_attrs(item, 'pl')
            playqueue = PlayQueue.create(self.plex, playlist)
            self._load_attrs(playqueue, 'pq')

    def _parse_sync(self):
        # TODO: Get plexattrs._parse_sync() working.
        pass

    def _load_attrs(self, obj, cat=None):
        if isinstance(obj, (list, tuple)):
            return [self._parse_objects(item, cat) for item in obj]
        self._parse_objects(obj, cat)

    def _parse_objects(self, obj, cat=None):
        clsname = '%s.%s' % (obj.__module__, obj.__class__.__name__)
        clsname = clsname.replace('plexapi.', '')
        if self.clsnames and clsname not in self.clsnames:
            return None
        self._print_the_little_dot()
        if clsname not in self.attrs:
            self.attrs[clsname] = copy.deepcopy(NAMESPACE)
        self.attrs[clsname]['total'] += 1
        self._load_xml_attrs(clsname, obj._data, self.attrs[clsname]['xml'],
            self.attrs[clsname]['examples'], self.attrs[clsname]['categories'], cat)
        self._load_obj_attrs(clsname, obj, self.attrs[clsname]['obj'],
            self.attrs[clsname]['docs'])

    def _print_the_little_dot(self):
        self.total += 1
        if not self.total % 100:
            sys.stdout.write('.')
            if not self.total % 8000:
                sys.stdout.write('\n')
            sys.stdout.flush()

    def _load_xml_attrs(self, clsname, elem, attrs, examples, categories, cat):
        if elem is None: return None
        for attr in sorted(elem.attrib.keys()):
            attrs[attr] += 1
            if cat: categories[attr].add(cat)
            if elem.attrib[attr] and len(examples[attr]) <= self.opts.examples:
                examples[attr].add(elem.attrib[attr])
            for subelem in elem:
                attrname = TAGATTRS.get(subelem.tag, '%ss' % subelem.tag.lower())
                attrs['%s[]' % attrname] += 1

    def _load_obj_attrs(self, clsname, obj, attrs, docs):
        if clsname in STOP_RECURSING_AT: return None
        if isinstance(obj, PlexObject) and clsname not in DONT_RELOAD:
            self._safe_reload(obj)
        alldocs = '\n\n'.join(self._all_docs(obj.__class__))
        for attr, value in obj.__dict__.items():
            if value is None or isinstance(value, (str, bool, float, int, datetime)):
                if not attr.startswith('_') and attr not in IGNORES.get(clsname, []):
                    attrs[attr] += 1
                    if re.search('\s{8}%s\s\(.+?\)\:' % attr, alldocs) is not None:
                        docs[attr] += 1
            if isinstance(value, list):
                if not attr.startswith('_') and attr not in IGNORES.get(clsname, []):
                    if value and isinstance(value[0], PlexObject):
                        attrs['%s[]' % attr] += 1
                        [self._parse_objects(obj) for obj in value]

    def _all_docs(self, cls, docs=None):
        import inspect
        docs = docs or []
        if cls.__doc__ is not None:
            docs.append(cls.__doc__)
        for parent in inspect.getmro(cls):
            if parent != cls:
                docs += self._all_docs(parent)
        return docs

    def print_report(self):
        total_attrs = 0
        for clsname in sorted(self.attrs.keys()):
            if self._clsname_match(clsname):
                meta = self.attrs[clsname]
                count = meta['total']
                print(_('\n%s (%s)\n%s' % (clsname, count, '-' * 30), 'yellow'))
                attrs = sorted(set(list(meta['xml'].keys()) + list(meta['obj'].keys())))
                for attr in attrs:
                    state = self._attr_state(clsname, attr, meta)
                    count = meta['xml'].get(attr, 0)
                    categories = ','.join(meta['categories'].get(attr, ['--']))
                    examples = '; '.join(list(meta['examples'].get(attr, ['--']))[:3])[:80]
                    print('%7s  %3s  %-30s  %-20s  %s' % (count, state, attr, categories, examples))
                    total_attrs += count
        print(_('\nSUMMARY\n%s' % ('-' * 30), 'yellow'))
        print('%7s  %3s  %3s  %3s  %-20s  %s' % ('total', 'new', 'old', 'doc', 'categories', 'clsname'))
        for clsname in sorted(self.attrs.keys()):
            if self._clsname_match(clsname):
                print('%7s  %12s  %12s  %12s  %s' % (self.attrs[clsname]['total'],
                    _(self.attrs[clsname]['new'] or '', 'cyan'),
                    _(self.attrs[clsname]['old'] or '', 'red'),
                    _(self.attrs[clsname]['doc'] or '', 'purple'),
                    clsname))
        print('\nPlex Version     %s' % self.plex.version)
        print('PlexAPI Version  %s' % plexapi.VERSION)
        print('Total Objects    %s' % sum([x['total'] for x in self.attrs.values()]))
        print('Runtime          %s min\n' % self.runtime)

    def _clsname_match(self, clsname):
        if not self.clsnames:
            return True
        for cname in self.clsnames:
            if cname.lower() in clsname.lower():
                return True
        return False

    def _attr_state(self, clsname, attr, meta):
        if attr in meta['xml'].keys() and attr not in meta['obj'].keys():
            self.attrs[clsname]['new'] += 1
            return _('new', 'blue')
        if attr not in meta['xml'].keys() and attr in meta['obj'].keys():
            self.attrs[clsname]['old'] += 1
            return _('old', 'red')
        if attr not in meta['docs'].keys() and attr in meta['obj'].keys():
            self.attrs[clsname]['doc'] += 1
            return _('doc', 'purple')
        return _('   ', 'green')

    def _safe_connect(self, elem):
        try:
            return elem.connect()
        except:
            return None

    def _safe_reload(self, elem):
        try:
            elem.reload()
        except:
            pass


def _(text, color):
    FMTSTR = '\033[%dm%s\033[0m'
    COLORS = {'blue':34, 'cyan':36, 'green':32, 'grey':30, 'purple':35, 'red':31, 'white':37, 'yellow':33}
    return FMTSTR % (COLORS[color], text)


if __name__ == '__main__':
    print(__doc__)
    parser = argparse.ArgumentParser(description='resize and copy starred photos')
    parser.add_argument('-f', '--force', default=False, action='store_true', help='force a full refresh of attributes.')
    parser.add_argument('-m', '--max', default=99999, help='max number of objects to load.')
    parser.add_argument('-e', '--examples', default=10, help='max number of example values to load.')
    parser.add_argument('-c', '--clsnames', default='', help='only report the following class names')
    opts = parser.parse_args()
    # Load the plexattrs object
    plexattrs = None
    if not opts.force and os.path.exists(CACHEPATH):
        with open(CACHEPATH, 'rb') as handle:
            plexattrs = pickle.load(handle)
            plexattrs.clsnames = [c for c in opts.clsnames.split(',') if c]
    if not plexattrs:
        plexattrs = PlexAttributes(opts).run()
        with open(CACHEPATH, 'wb') as handle:
            pickle.dump(plexattrs, handle)
    # Print Report
    plexattrs.print_report()
