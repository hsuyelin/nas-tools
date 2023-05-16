Performance
===========

By default, complex objects are returned from some endpoints. These objects allow for accessing the response's items as attributes and include methods for contextually relevant actions (such as ``start()`` and ``stop()`` for a torrent, for example).

This comes at the cost of performance, though. Generally, this cost isn't large; however, some endpoints, such as ``torrents_files()``, may need to convert a large payload and the cost can be significant.

This client can be configured to always return only the simple JSON if desired. Simply set ``SIMPLE_RESPONSES=True`` when instantiating the client.

.. code:: python

    qbt_client = qbittorrentapi.Client(
        host='localhost:8080',
        username='admin',
        password='adminadmin',
        SIMPLE_RESPONSES=True,
    )

Alternatively, ``SIMPLE_RESPONSES`` can be set to ``True`` to return the simple JSON only for an individual method call.

.. code:: python

    qbt_client.torrents.files(torrent_hash='...', SIMPLE_RESPONSES=True)
