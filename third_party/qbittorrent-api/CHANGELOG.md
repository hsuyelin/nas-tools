Change log
==========
### v2023.4.46 (14 apr 2023)
- Fix building docs after implementing ``src-layout``

### v2023.4.45 (11 apr 2023)
- Add the ``TrackerStatus`` Enum to identify tracker statuses from ``torrents/trackers``

### v2023.3.44 (09 mar 2023)
- Add support for torrent status filters ``seeding``, ``moving``, ``errored``, and ``checking``

### v2023.2.43 (27 feb 2023)
- Advertise support for qBittorrent v4.5.2

### v2023.2.42 (13 feb 2023)
- Advertise support for qBittorrent v4.5.1

### v2023.2.41 (8 feb 2023)
- Remove dependence on qBittorrent authentication cookie being named ``SID``
- Minor typing fixes

### v2022.11.40 (27 nov 2022)
- Support qBittorrent v4.5.0 release
- Add support for ``torrents/export``
- Implement new ``transfer/setSpeedLimitsMode`` in place of existing ``transfer/toggleSpeedLimitsMode``
- Add support for ``stopCondition`` in ``torrents/add``
- Update typing to be complete, accurate, and shipped with the package

### v2022.10.39 (26 oct 2022)
- Advertise support for Python 3.11

### v2022.8.38 (31 aug 2022)
- Advertise support for qBittorrent v4.4.5

### v2022.8.37 (24 aug 2022)
- Advertise support for qBittorrent v4.4.4

### v2022.8.36 (15 aug 2022)
- Comply with enforced HTTP method requirements from qBittorrent

### v2022.8.35 (13 aug 2022)
- Remove ``PYTHON_`` prefix for configuration environment variables

### v2022.8.34 (11 aug 2022)
- Add ``setuptools`` as an explicit dependency for ``pkg_resources.parse_version()``

### v2022.7.33 (27 jul 2022)
- Reorder class hierarchy to allow independent MixIn use
- Clean up typing annotations
- Optimize Dictionary and List initializations
- Rename Alias decorator to alias for better conformity

### v2022.5.32 (30 may 2022)
- Implement pre-commit checks
- Advertise support for qBittorrent v4.4.3.1

### v2022.5.31 (24 may 2022)
- Advertise support for qBittorrent v4.4.3
- Revamp GitHub CI
- Reorg ``Request`` for some more clarity (hopefully)

### v2022.4.30 (3 apr 2022)
- Stop advertising support for Python 3.6 (EOL 12/2021)
- Publish to PyPI using API token and cleanup GitHub Action scripts

### v2022.3.29 (25 mar 2022)
- Advertise support for qBittorrent v4.4.2

### v2022.2.28 (17 feb 2022)
- Advertise support for qBittorrent v4.4.1
- qBittorrent reverted the category dictionary key ``savePath`` back to ``save_path``

### v2022.1.27 (9 jan 2022)
- Support for qBittorrent v4.4.0
- ``torrents/info`` results can now be filtered by a torrent tag
- Added new torrent state "Forced Metadata Downloading"
- Support per-torrent/per-category "download folder"

### v2021.12.26 (11 dec 2021)
- Stop sending ``Origin`` and ``Referer`` headers (Fixes #63)

### v2021.12.25 (10 dec 2021)
- Close files that are opened and sent to Requests when adding torrents from files
- Enable warnings for tests and explicitly close Requests Sessions to prevent (mostly spurious) ResourceWarnings

### v2021.12.24 (3 dec 2021)
- Add Type Hints for all public and private functions, methods, and variables
- Support HTTP timeouts as well as arbitrary Requests configurations

### v2021.8.23 (28 aug 2021)
- Advertise support for qBittorrent v4.3.8
- Drop support for Python 3.5

### v2021.5.22 (12 may 2021)
- Support for qBittorrent v4.3.5
- ``torrents/files`` includes ``index`` for each file; ``index`` officially replaces ``id`` but ``id`` will still be populated

### v2021.5.21 (1 may 2021)
- Allow users to force a specific communications scheme with ``FORCE_SCHEME_FROM_HOST`` (fixes #54)

### v2021.4.20 (11 apr 2021)
- Add support for ratio limit and seeding time limit when adding torrents

### v2021.4.19 (8 apr 2021)
- Update license in setup to match gpl->mit license change on GitHub

### v2021.3.18 (13 mar 2021)
- Replace ``TorrentStates.FORCE_DOWNLOAD='forceDL'`` with ``TorrentStates.FORCED_DOWNLOAD='forcedDL'``

### v2021.2.17 (7 feb 2021)
- Generally refactor ``requests.py`` so it's better and easier to read
- Persist a Requests Session between API calls instead of always creating a new one...small perf benefit
- Move auth endpoints back to a dedicated module
- Since ``attrdict`` is apparently going to break in Python 3.10 and it is no longer maintained, I've vendored a modified version (fixes #45).
- Created ``handle_hashes`` decorator to hide the cruft of continuing to support hash and hashes arguments

### v2021.1.16 (26 jan 2021)
- Support qBittorrent v4.3.3 and Web API v2.7 (...again)
- New ``torrents/renameFile`` and ``torrents/renameFolder`` endpoints
- Retrieve app api version when needed instead of caching
- Stop verifying and removing individual parameters when they aren't supported

### v2020.12.15 (27 dec 2020)
- Support qBittorrent v4.3.2 and Web API v2.7
- ``torrents/add`` supports adding torrents with tags via ``tags`` parameter
- ``app/preferences`` supports toggling internationalized domain name (IDN) support via ``idn_support_enabled``
- BREAKING CHANGE: for ``torrents/add``, ``is_root_folder`` (or ``root_folder``) is superseded by ``content_layout``
- For ``torrents/delete``, ``delete_files`` now defaults to ``False`` instead of required being explicitly passed

### v2020.12.14 (6 dec 2020)
- Add support for non-standard API endpoint paths (Fixes #37)
- Allows users to leverage this client when qBittorrent is configured behind a reverse proxy.
  - For instance, if the Web API is being exposed at "http://localhost/qbt/", then users can instantiate via ``Client(host='localhost/qbt')`` and all API endpoint paths will be prefixed with "/qbt".
- Additionally, the scheme (i.e. http or https) from the user will now be respected as the first choice for which scheme is used to communicate with qBittorrent.
  - However, users still don't need to even specify a scheme; it'll be automatically determined on the first connection to qBittorrent.
- Neither of these should be breaking changes, but if you're instantiating with an incorrect scheme or an irrelevant path, you may need to prevent doing that now.

### v2020.11.13 (29 nov 2020)
- Support qBittorrent v4.3.1 and Web API v2.6.1
- Path of torrent content now available via ``content_path`` from ``torrents/info``

### v2020.11.12 (16 nov 2020)
- Fix support for raw bytes for ``torrent_files`` in ``torrents_add()`` for Python 3. Fixes #34.

### v2020.10.11 (29 oct 2020)
- Support qBittorrent v4.3.0.1 and Web API v2.6
- Due to qBittorrent changes, ``search/categories`` no longer returns anything and ``rss/renameRule`` works again

### v2020.10.10 (7 oct 2020)
- Advertise support for Python 3.9

### v2020.9.9 (12 sept 2020)
- Only request ``enum34`` for Python 2

### v2020.8.8 (14 aug 2020)
- Support adding torrents from raw torrent files as bytes or file handles. Fixes #23.
- Introduce ``TorrentStates`` enum for qBittorrent list of torrent states.

### v2020.7.7 (26 jul 2020)
- Update tests and misc small fixes.

### v2020.7.6 (25 jul 2020)
- Re-release of v2020.7.5.

### v2020.7.5 (25 jul 2020)
- Add RTD documentation.

### v2020.6.4 (9 jun 2020)
- Bug fix release. Reorganized code and classes to be more logical.
- Started returning None from many methods that were returning Requests Responses.
- Content-Length header is now explicitly sent as "0" for any POSTs without a body.
- Endpoint input parameters ``hash`` and ``hashes`` are renamed to ``torrent_hash`` and ``torrent_hashes``. ``hash`` and ``hashes`` remain supported.
- ``search_uninstall_plugin`` now works. search_enable_plugin now supports multiple plugins.
- ``Torrent.download_limit`` now only return the value instead of a dictionary. ``Torrent.upload_limit`` now works.
- Drop advertising Python 2.6 and 3.4 support; add PyPy3 support.
- Implement test suite and CI that can test all supported qBittorrent versions on all pythons.

### v2020.5.3 (11 may 2020)
- Include currently supported qBittorrent version in README. Fixes #11.

### v2020.4.2 (25 apr 2020)
- Add support for ``rss/markAsRead`` and ``rss/matchingArticles``. Added in v2.5.1. Fixes #10

### v2020.4.1 (25 apr 2020)
- Add ``stalled()``, ``stalled_uploading()``, and ``stalled_downloading()`` to ``torrents.info`` interaction. Added in Web API v2.4.1.
- Implement torrent file renaming. Added in Web API v2.4.0. Fixes #3.
- Since versioning was botched last release, implement calendar versioning.
- List of files returned from ``torrents_files()`` now contains file ID in ``id``.

### v6.0.0 (22 apr 2020)
- Performance gains for responses with payloads...especially for large payloads.
- Fixes #6. Adds support for ``SIMPLE_RESPONSES`` for the entire client and individual methods.

### v0.5.2 (19 apr 2020)
- Fixes #8. Remove whitespace from in setPreferences requests for older qBittorrent versions.

### v0.5.1 (2 jan 2020)
- Add Python3.8 version for PyPI
- Move project from beta to stable for PyPI

### v0.5.0 (2 jan 2020)
- Make Web API URL derivation more robust...thereby allowing the client to actually work on Python3.8 (#5)
- Allow port to be discretely specified during Client instantiation (#4)
- Enhance request retry logic and expose retry configuration

### v0.4.2 (5 dec 2019)
- Improve organization and clarity of README
- Better document exceptions
- Clarify torrent file handling exceptions better with proper exceptions
- Clean up the request wrapper exception handling
- Fix HTTP 404 handling to find and return problematic torrent hashes

### v0.4.1 (4 dec 2019)
- Round out support for tags with qBittorrent v4.2.0 release
- Remove upper-bound version requirements for ``requests`` and ``urllib3``

### v0.4 (4 dec 2019)
- Support for qBittorrent v4.2.0 release
- Add support for ``app/buildInfo``
- Add support for ``transfer/banPeers`` and ``torrents/addPeers``
- Add support for ``torrents/addTags``, ``torrents/removeTags``, ``torrents/tags``, ``torrents/createTags``, and ``torrents/deleteTags``

### v0.3.3 (29 sept 2019)
- Fix useAutoTMM to autoTMM for ``client.torrents_add()`` so auto torrent management works
- Add support to refresh RSS items introduced in qBittorrent v4.1.8

### v0.3.2 (28 jun 2019)
- Restore python 2 compatibility
- Allow exceptions to be imported directly from package instead of only exceptions module

### v0.3 (1 jun 2019)
- Finalized interaction layer interfaces

### v0.2 (13 may 2019)
- Introduced the "interaction layer" for transparent interaction with the qBittorrent API.

### v0.1 (7 may 2019)
- Complete implementation of qBittorrent WebUI API 2.2.
- Each API endpoint is available via the ``Client`` class.
- Automatic re-login is supported in the event of login expiration.
