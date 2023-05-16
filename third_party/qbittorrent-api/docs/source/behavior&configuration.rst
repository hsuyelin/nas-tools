Behavior & Configuration
================================

Untrusted WebUI Certificate
***************************
* qBittorrent allows you to configure HTTPS with an untrusted certificate; this commonly includes self-signed certificates.
* When using such a certificate, instantiate Client with ``VERIFY_WEBUI_CERTIFICATE=False`` or set environment variable ``QBITTORRENTAPI_DO_NOT_VERIFY_WEBUI_CERTIFICATE`` to a non-null value.
* Failure to do this for will cause connections to qBittorrent to fail.
* As a word of caution, doing this actually does turn off certificate verification. Therefore, for instance, potential man-in-the-middle attacks will not be detected and reported (since the error is suppressed). However, the connection will remain encrypted.

.. code:: python

    qbt_client = Client(..., VERIFY_WEBUI_CERTIFICATE=False}

Host, Username and Password
***************************
* The authentication credentials can be provided when instantiating ``Client``:

.. code:: python

    qbt_client = Client(host="localhost:8080", username='...', password='...')

* The credentials can also be specified after ``Client`` is created but calling ``auth_log_in()`` is not strictly necessary to authenticate the client; this will happen automatically for any API request.

.. code:: python

    qbt_client.auth_log_in(username='...', password='...')

* Alternatively, the credentials can be specified in environment variables:

  * ``QBITTORRENTAPI_HOST``
  * ``QBITTORRENTAPI_USERNAME``
  * ``QBITTORRENTAPI_PASSWORD``

Requests Configuration
**********************
* The `Requests <https://requests.readthedocs.io/en/latest/>`_ package is used to issue HTTP requests to qBittorrent to facilitate this API.
* Much of ``Requests`` configuration for making HTTP calls can be controlled with parameters passed along with the request payload.
* For instance, HTTP Basic Authorization credentials can be provided via ``auth``, timeouts via ``timeout``, or Cookies via ``cookies``. See `Requests documentation <https://requests.readthedocs.io/en/latest/api/#requests.request>`_ for full details.
* These parameters are exposed here in two ways; the examples below tell ``Requests`` to use a connect timeout of 3.1 seconds and a read timeout of 30 seconds.
* When you instantiate ``Client``, you can specify the parameters to use in all HTTP requests to qBittorrent:

.. code:: python

    qbt_client = Client(..., REQUESTS_ARGS={'timeout': (3.1, 30)}

* Alternatively, parameters can be specified for individual requests:

.. code:: python

    qbt_client.torrents_info(..., requests_args={'timeout': (3.1, 30))

Additional HTTP Headers
***********************
* For consistency, HTTP Headers can be specified using the method above; for backwards compatibility, the methods below are supported as well.
* Either way, these additional headers will be incorporated (using clobbering) into the rest of the headers to be sent.
* To send a custom HTTP header in all requests made from an instantiated client, declare them during instantiation:

.. code:: python

    qbt_client = Client(..., EXTRA_HEADERS={'X-My-Fav-Header': 'header value')

* Alternatively, you can send custom headers in individual requests:

.. code:: python

    qbt_client.torrents.add(..., headers={'X-My-Fav-Header': 'header value')

Unimplemented API Endpoints
***************************
* Since the qBittorrent Web API has evolved over time, some endpoints may not be available from the qBittorrent host.
* By default, if a call is made to endpoint that doesn't exist for the version of the qBittorrent host (e.g., the Search endpoints were introduced in Web API v2.1.1), there's a debug logger output and None is returned.
* To raise ``NotImplementedError`` instead, instantiate Client with:

.. code:: python

    qbt_client = Client(..., RAISE_NOTIMPLEMENTEDERROR_FOR_UNIMPLEMENTED_API_ENDPOINTS=True)

qBittorrent Version Checking
****************************
* It is also possible to either raise an Exception for qBittorrent hosts that are not "fully" supported or manually check for support.
* The most likely situation for this to occur is if the qBittorrent team publishes a new release but its changes have not been incorporated in to this client yet.
* Instantiate Client like below to raise ``UnsupportedQbittorrentVersion`` exception for versions not fully supported:

.. code:: python

    qbt_client = Client(..., RAISE_ERROR_FOR_UNSUPPORTED_QBITTORRENT_VERSIONS=True)

* Additionally, the :doc:`qbittorrentapi.Version <apidoc/version>` class can be used for manual introspection of the versions.

.. code:: python

    Version.is_app_version_supported(qbt_client.app.version)

Disable Logging Debug Output
****************************
* Instantiate Client with ``DISABLE_LOGGING_DEBUG_OUTPUT=True`` or manually disable logging for the relevant packages:

.. code:: python

    logging.getLogger('qbittorrentapi').setLevel(logging.INFO)
    logging.getLogger('requests').setLevel(logging.INFO)
    logging.getLogger('urllib3').setLevel(logging.INFO)
