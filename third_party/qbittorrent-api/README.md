<div align="center">

qBittorrent Web API Client
================================

Python client implementation for qBittorrent Web API

[![GitHub Workflow Status (branch)](https://img.shields.io/github/checks-status/rmartin16/qbittorrent-api/main?style=flat-square)](https://github.com/rmartin16/qbittorrent-api/actions?query=branch%3Amain) [![Codecov branch](https://img.shields.io/codecov/c/gh/rmartin16/qbittorrent-api/main?style=flat-square)](https://app.codecov.io/gh/rmartin16/qbittorrent-api) [![Coverity Scan](https://img.shields.io/coverity/scan/21227?style=flat-square)](https://scan.coverity.com/projects/rmartin16-qbittorrent-api) [![Codacy grade](https://img.shields.io/codacy/grade/ef2975376e834af1910632cb76d05832?style=flat-square)](https://app.codacy.com/gh/rmartin16/qbittorrent-api/dashboard) [![PyPI](https://img.shields.io/pypi/v/qbittorrent-api?style=flat-square)](https://pypi.org/project/qbittorrent-api/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/qbittorrent-api?style=flat-square)](https://pypi.org/project/qbittorrent-api/)

</div>

Currently supports qBittorrent [v4.5.2](https://github.com/qbittorrent/qBittorrent/releases/tag/release-4.5.2) (Web API v2.8.19) released on Feb 27, 2023.

User Guide and API Reference available on [Read the Docs](https://qbittorrent-api.readthedocs.io/).

Features
------------
* The entire qBittorrent [Web API](https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)) is implemented.
* qBittorrent version checking for an endpoint's existence/features is automatically handled.
* All Python versions are supported.
* If the authentication cookie expires, a new one is automatically requested in line with any API call.

Installation
------------
Install via pip from [PyPI](https://pypi.org/project/qbittorrent-api/)
```bash
pip install qbittorrent-api
```

Getting Started
---------------
```python
import qbittorrentapi

# instantiate a Client using the appropriate WebUI configuration
qbt_client = qbittorrentapi.Client(
    host='localhost',
    port=8080,
    username='admin',
    password='adminadmin',
)

# the Client will automatically acquire/maintain a logged-in state
# in line with any request. therefore, this is not strictly necessary;
# however, you may want to test the provided login credentials.
try:
    qbt_client.auth_log_in()
except qbittorrentapi.LoginFailed as e:
    print(e)

# display qBittorrent info
print(f'qBittorrent: {qbt_client.app.version}')
print(f'qBittorrent Web API: {qbt_client.app.web_api_version}')
for k,v in qbt_client.app.build_info.items(): print(f'{k}: {v}')

# retrieve and show all torrents
for torrent in qbt_client.torrents_info():
    print(f'{torrent.hash[-6:]}: {torrent.name} ({torrent.state})')

# pause all torrents
qbt_client.torrents.pause.all()
```
