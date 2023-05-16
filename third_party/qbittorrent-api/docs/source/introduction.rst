Introduction
======================

.. |github ci| image:: https://img.shields.io/github/checks-status/rmartin16/qbittorrent-api/main?style=flat-square
   :target: https://github.com/rmartin16/qbittorrent-api/actions?query=branch%3Amain
.. |codecov| image:: https://img.shields.io/codecov/c/gh/rmartin16/qbittorrent-api/main?style=flat-square
   :target: https://app.codecov.io/gh/rmartin16/qbittorrent-api
.. |coverity| image:: https://img.shields.io/coverity/scan/21227?style=flat-square
   :target: https://scan.coverity.com/projects/rmartin16-qbittorrent-api
.. |codacy| image:: https://img.shields.io/codacy/grade/ef2975376e834af1910632cb76d05832?style=flat-square
   :target: https://app.codacy.com/gh/rmartin16/qbittorrent-api/dashboard

.. |pypi| image:: https://img.shields.io/pypi/v/qbittorrent-api?style=flat-square
   :target: https://pypi.org/project/qbittorrent-api/
.. |pypi versions| image:: https://img.shields.io/pypi/pyversions/qbittorrent-api?style=flat-square
   :target: https://pypi.org/project/qbittorrent-api/
.. |pypi implementations| image:: https://img.shields.io/pypi/implementation/qbittorrent-api?style=flat-square
   :target: https://pypi.org/project/qbittorrent-api/
.. |pypi downloads| image:: https://img.shields.io/pypi/dw/qbittorrent-api?color=blue&style=flat-square
   :target: https://pypi.org/project/qbittorrent-api/

|github ci| |codecov| |coverity| |codacy|

|pypi| |pypi versions| |pypi implementations| |pypi downloads|

Python client implementation for qBittorrent Web API.

Currently supports qBittorrent `v4.5.2 <https://github.com/qbittorrent/qBittorrent/releases/tag/release-4.5.2>`_ (Web API v2.8.19) released on Feb 27, 2023.

Features
------------
- The entire qBittorrent `Web API <https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)>`_ is implemented.
- qBittorrent version checking for an endpoint's existence/features is automatically handled.
- All Python versions are supported.
- If the authentication cookie expires, a new one is automatically requested in line with any API call.

Installation
------------
* Install via pip from `PyPI <https://pypi.org/project/qbittorrent-api/>`_:

.. code:: console

    pip install qbittorrent-api

* Install a specific release (e.g. ``v2022.8.34``):

.. code:: console

    pip install git+https://github.com/rmartin16/qbittorrent-api.git@v2022.8.34#egg=qbittorrent-api

* Install direct from ``main``:

.. code:: console

    pip install git+https://github.com/rmartin16/qbittorrent-api.git@main#egg=qbittorrent-api

* Enable WebUI in qBittorrent: Tools -> Preferences -> Web UI
* If the Web API will be exposed to the Internet, follow the `recommendations <https://github.com/qbittorrent/qBittorrent/wiki/Linux-WebUI-HTTPS-with-Let's-Encrypt-certificates-and-NGINX-SSL-reverse-proxy>`_.

Getting Started
---------------
.. code:: python

   import qbittorrentapi

   # instantiate a Client using the appropriate WebUI configuration
   qbt_client = qbittorrentapi.Client(
       host='localhost',
       port=8080,
       username='admin',
       password='adminadmin'
    )

   # the Client will automatically acquire/maintain a logged in state in line with any request.
   # therefore, this is not necessary; however, you many want to test the provided login credentials.
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

Usage
-----
First, the Web API endpoints are organized in to eight namespaces.

* Authentication (``auth``)
* Application (``app``)
* Log (``log``)
* Sync (``sync``)
* Transfer (``transfer``)
* Torrent Management (``torrents``)
* RSS (``rss``)
* Search (``search``)

Second, this client has two modes of interaction with the qBittorrent Web API.

Each Web API endpoint is implemented one-to-one as a method of the instantiated client.

.. code:: python

    import qbittorrentapi
    qbt_client = qbittorrentapi.Client(host='localhost:8080', username='admin', password='adminadmin')
    qbt_client.app_version()
    qbt_client.rss_rules()
    qbt_client.torrents_info()
    qbt_client.torrents_resume(torrent_hashes='...')
    # and so on

However, a more robust interface to the endpoints is available via each namespace. This is intended to provide a more seamless and intuitive interface to the Web API.

.. code:: python

    import qbittorrentapi
    qbt_client = qbittorrentapi.Client(host='localhost:8080', username='admin', password='adminadmin')
    # changing a preference
    is_dht_enabled = qbt_client.app.preferences.dht
    qbt_client.app.preferences = dict(dht=not is_dht_enabled)
    # stopping all torrents
    qbt_client.torrents.pause.all()
    # retrieve different views of the log
    qbt_client.log.main.warning()
    qbt_client.log.main.normal()

Finally, some of the objects returned by the client support methods of their own. This is most pronounced for torrents themselves.

.. code:: python

    import qbittorrentapi
    qbt_client = qbittorrentapi.Client(host='localhost:8080', username='admin', password='adminadmin')

    for torrent in qbt_client.torrents.info.active():
        torrent.set_location(location='/home/user/torrents/')
        torrent.reannounce()
        torrent.upload_limit = -1
