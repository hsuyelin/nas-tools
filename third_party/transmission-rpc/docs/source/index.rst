.. transmission-rpc documentation master file, created by
    sphinx-quickstart on Fri Oct  5 09:29:21 2018.
    You can adapt this file completely to your liking, but it should at least
    contain the root `toctree` directive.

Welcome to transmission-rpc's documentation!
============================================

:code:`transmission-rpc` is a python3 library
to help your control your transmission daemon remotely.

quick start
-------------------------

.. literalinclude:: examples/quick-start.py

.. seealso::

   :py:meth:`transmission_rpc.client.Client.add_torrent`

Example
=======

Filter files

.. literalinclude:: examples/change_torrent_file.py

Move Torrent Data

.. literalinclude:: examples/move_torrent_data.py

Set Upload/Download Speed Limit

.. literalinclude:: examples/set_download_upload_speed.py

Arguments
-------------------

Each method has it own arguments.
You can pass arguments as kwargs when you call methods.

But in python, :code:`-` can't be used in a variable name,
so you need to replace :code:`-` with :code:`_`.

For example, :code:`torrent-add` method support arguments :code:`download-dir`,
you should call method like this.

.. code-block :: python

    from transmission_rpc import Client

    Client().add_torrent(torrent_url, download_dir='/path/to/download/dir')

:code:`transmission-rpc` will put
:code:`{"download-dir": "/path/to/download/dir"}` in arguments.


you can find rpc version by transmission version from
`transmission rpc docs <https://github.com/transmission/transmission/blob/main/docs/rpc-spec.md#5-protocol-versions>`_


.. toctree::
    :maxdepth: 2
    :caption: Contents:

    client.rst
    torrent.rst
    const.rst
    session.rst
    errors.rst
    utils.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
