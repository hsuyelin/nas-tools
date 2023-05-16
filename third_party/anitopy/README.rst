=======
Anitopy
=======

Anitopy is a Python library for parsing anime video filenames. It's simple to use and it's based on the C++ library `Anitomy <https://github.com/erengy/anitomy>`_.

Example
-------
The following filename...

::

    [TaigaSubs]_Toradora!_(2008)_-_01v2_-_Tiger_and_Dragon_[1280x720_H.264_FLAC][1234ABCD].mkv

...can be parsed using the following code:

.. code-block:: python

    >>> import anitopy
    >>> anitopy.parse('[TaigaSubs]_Toradora!_(2008)_-_01v2_-_Tiger_and_Dragon_[1280x720_H.264_FLAC][1234ABCD].mkv')
    {
        'anime_title': 'Toradora!',
        'anime_year': '2008',
        'audio_term': 'FLAC',
        'episode_number': '01',
        'episode_title': 'Tiger and Dragon',
        'file_checksum': '1234ABCD',
        'file_extension': 'mkv',
        'file_name': '[TaigaSubs]_Toradora!_(2008)_-_01v2_-_Tiger_and_Dragon_[1280x720_H.264_FLAC][1234ABCD].mkv',
        'release_group': 'TaigaSubs',
        'release_version': '2',
        'video_resolution': '1280x720',
        'video_term': 'H.264'
    }

The :code:`parse` function receives a string and returns a dictionary containing all found elements. It can also receive parsing options, this will be explained below.

Installation
------------

To install Anitopy, simply use pip:

.. code-block:: bash

    pip install anitopy

Or download the source code and inside the source code's folder run:

.. code-block:: bash

    python setup.py install

Options
-------

The :code:`parse` function can receive the :code:`options` parameter. E.g.:

.. code-block:: python

    >>> import anitopy
    >>> anitopy_options = {'allowed_delimiters': ' '}
    >>> anitopy.parse('DRAMAtical Murder Episode 1 - Data_01_Login', options=anitopy_options)
    {
        'anime_title': 'DRAMAtical Murder',
        'episode_number': '1',
        'episode_title': 'Data_01_Login',
        'file_name': 'DRAMAtical Murder Episode 1 - Data_01_Login'
    }

If the default options had been used, the parser would have considered :code:`_` as a delimiter and replaced it with space in the episode title.

The options contain the following attributes:

+----------------------+-----------------+-----------------------------------------------------------------+-------------------+
| **Attribute name**   | **Type**        | **Description**                                                 | **Default value** |
+----------------------+-----------------+-----------------------------------------------------------------+-------------------+
| allowed_delimiters   | string          | The list of character to be considered as delimiters.           | ' _.&+,|'         |
+----------------------+-----------------+-----------------------------------------------------------------+-------------------+
| ignored_strings      | list of strings | A list of strings to be removed from the filename during parse. | []                |
+----------------------+-----------------+-----------------------------------------------------------------+-------------------+
| parse_episode_number | boolean         | If the episode number should be parsed.                         | True              |
+----------------------+-----------------+-----------------------------------------------------------------+-------------------+
| parse_episode_title  | boolean         | If the episode title should be parsed.                          | True              |
+----------------------+-----------------+-----------------------------------------------------------------+-------------------+
| parse_file_extension | boolean         | If the file extension should be parsed.                         | True              |
+----------------------+-----------------+-----------------------------------------------------------------+-------------------+
| parse_release_group  | boolean         | If the release group should be parsed.                          | True              |
+----------------------+-----------------+-----------------------------------------------------------------+-------------------+
