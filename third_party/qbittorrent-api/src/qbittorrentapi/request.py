from copy import deepcopy
from json import loads
from logging import NullHandler
from logging import getLogger
from os import environ
from time import sleep

try:  # python 3
    from collections.abc import Iterable
    from urllib.parse import urljoin
    from urllib.parse import urlparse
except ImportError:  # python 2  # pragma: no cover
    from collections import Iterable
    from urlparse import urljoin
    from urlparse import urlparse

import six
from requests import Session
from requests import exceptions as requests_exceptions
from requests.adapters import HTTPAdapter
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from urllib3.util.retry import Retry

from qbittorrentapi.definitions import APINames
from qbittorrentapi.definitions import Dictionary
from qbittorrentapi.definitions import List
from qbittorrentapi.exceptions import APIConnectionError
from qbittorrentapi.exceptions import APIError
from qbittorrentapi.exceptions import Conflict409Error
from qbittorrentapi.exceptions import Forbidden403Error
from qbittorrentapi.exceptions import HTTP5XXError
from qbittorrentapi.exceptions import HTTPError
from qbittorrentapi.exceptions import InternalServerError500Error
from qbittorrentapi.exceptions import InvalidRequest400Error
from qbittorrentapi.exceptions import MethodNotAllowed405Error
from qbittorrentapi.exceptions import MissingRequiredParameters400Error
from qbittorrentapi.exceptions import NotFound404Error
from qbittorrentapi.exceptions import Unauthorized401Error
from qbittorrentapi.exceptions import UnsupportedMediaType415Error

logger = getLogger(__name__)
getLogger("qbittorrentapi").addHandler(NullHandler())


class URL(object):
    """Management for the qBittorrent Web API URL."""

    def __init__(self, client):
        self.client = client

    def build_url(self, api_namespace, api_method, headers, requests_kwargs):
        """
        Create a fully qualified URL for the API endpoint.

        :param api_namespace: the namespace for the API endpoint (e.g. ``torrents``)
        :param api_method: the specific method for the API endpoint (e.g. ``info``)
        :param headers: HTTP headers for request
        :param requests_kwargs: kwargs for any calls to Requests
        :return: fully qualified URL string for endpoint
        """
        # since base_url is guaranteed to end in a slash and api_path will never
        # start with a slash, this join only ever append to the path in base_url
        return urljoin(
            self.build_base_url(headers, requests_kwargs),
            self.build_url_path(api_namespace, api_method),
        )

    def build_base_url(self, headers, requests_kwargs=None):
        """
        Determine the Base URL for the Web API endpoints.

        A URL is only actually built here if it's the first time here or
        the context was re-initialized. Otherwise, the most recently
        built URL is used.

        If the user doesn't provide a scheme for the URL, it will try HTTP
        first and fall back to HTTPS if that doesn't work. While this is
        probably backwards, qBittorrent or an intervening proxy can simply
        redirect to HTTPS and that'll be respected.

        Additionally, if users want to augment the path to the API endpoints,
        any path provided here will be preserved in the returned Base URL
        and prefixed to all subsequent API calls.

        :param headers: HTTP headers for request
        :param requests_kwargs: arguments from user for HTTP ``HEAD`` request
        :return: base URL as a ``string`` for Web API endpoint
        """
        if self.client._API_BASE_URL is not None:
            return self.client._API_BASE_URL

        # Parse user host - urlparse requires some sort of scheme for parsing to work at all
        host = self.client.host
        if not host.lower().startswith(("http:", "https:", "//")):
            host = "//" + self.client.host
        base_url = urlparse(url=host)
        logger.debug("Parsed user URL: %r", base_url)

        # default to HTTP if user didn't specify
        user_scheme = base_url.scheme
        default_scheme = user_scheme or "http"
        alt_scheme = "https" if default_scheme == "http" else "http"

        # add port number if host doesn't contain one
        if self.client.port is not None and not base_url.port:
            host = "".join((base_url.netloc, ":", str(self.client.port)))
            base_url = base_url._replace(netloc=host)

        # detect whether Web API is configured for HTTP or HTTPS
        if not (user_scheme and self.client._FORCE_SCHEME_FROM_HOST):
            scheme = self.detect_scheme(
                base_url, default_scheme, alt_scheme, headers, requests_kwargs
            )
            base_url = base_url._replace(scheme=scheme)
            if user_scheme and user_scheme != base_url.scheme:
                logger.warning(
                    "Using '%s' instead of requested '%s' to communicate with qBittorrent",
                    base_url.scheme,
                    user_scheme,
                )

        # ensure URL always ends with a forward-slash
        base_url_str = base_url.geturl()
        if not base_url_str.endswith("/"):
            base_url_str += "/"
        logger.debug("Base URL: %s", base_url_str)

        # force a new session to be created now that the URL is known
        self.client._trigger_session_initialization()

        self.client._API_BASE_URL = base_url_str
        return base_url_str

    def detect_scheme(
        self, base_url, default_scheme, alt_scheme, headers, requests_kwargs
    ):
        """
        Determine if the URL endpoint is using HTTP or HTTPS.

        :param base_url: urllib :class:`~urllib.parse.ParseResult` URL object
        :param default_scheme: default scheme to use for URL
        :param alt_scheme: alternative scheme to use for URL if default doesn't work
        :param headers: HTTP headers for request
        :param requests_kwargs: kwargs for calls to Requests
        :return: scheme (i.e. ``HTTP`` or ``HTTPS``)
        """
        logger.debug("Detecting scheme for URL...")
        prefer_https = False
        for scheme in (default_scheme, alt_scheme):
            try:
                base_url = base_url._replace(scheme=scheme)
                r = self.client._session.request(
                    "head", base_url.geturl(), headers=headers, **requests_kwargs
                )
                scheme_to_use = urlparse(r.url).scheme
                break
            except requests_exceptions.SSLError:
                # an SSLError means that qBittorrent is likely listening on HTTPS
                # but the TLS connection is not trusted...so, if the attempt to
                # connect on HTTP also fails, this will tell us to switch back to HTTPS
                logger.debug("Encountered SSLError: will prefer HTTPS if HTTP fails")
                prefer_https = True
            except requests_exceptions.RequestException:
                logger.debug("Failed connection attempt with %s", scheme.upper())
        else:
            scheme_to_use = "https" if prefer_https else "http"
        # use detected scheme
        logger.debug("Using %s scheme", scheme_to_use.upper())
        return scheme_to_use

    def build_url_path(self, api_namespace, api_method):
        """
        Determine the full URL path for the API endpoint.

        :param api_namespace: the namespace for the API endpoint (e.g. torrents)
        :param api_method: the specific method for the API endpoint (e.g. info)
        :return: entire URL string for API endpoint
                 (e.g. ``http://localhost:8080/api/v2/torrents/info``
                 or ``http://example.com/qbt/api/v2/torrents/info``)
        """
        try:
            api_namespace = api_namespace.value
        except AttributeError:
            pass
        return "/".join(
            str(path_part or "").strip("/")
            for path_part in [self.client._API_BASE_PATH, api_namespace, api_method]
        )


class Request(object):
    """Facilitates HTTP requests to qBittorrent's Web API."""

    def __init__(self, host="", port=None, username=None, password=None, **kwargs):
        self.host = host
        self.port = port
        self.username = username or ""
        self._password = password or ""

        self._initialize_context()
        self._initialize_lesser(**kwargs)

        # URL management
        self._url = URL(client=self)

        # turn off console-printed warnings about SSL certificate issues.
        # these errors are only shown once the user has explicitly allowed
        # untrusted certs via VERIFY_WEBUI_CERTIFICATE...so printing them
        # in a console isn't particularly useful.
        if not self._VERIFY_WEBUI_CERTIFICATE:
            disable_warnings(InsecureRequestWarning)

    def _initialize_context(self):
        """
        Initialize and/or reset communications context with qBittorrent.

        This is necessary on startup or when the authorization cookie needs
        to be replaced...perhaps because it expired, qBittorrent was
        restarted, significant settings changes, etc.
        """
        logger.debug("Re-initializing context...")
        # base path for all API endpoints
        self._API_BASE_PATH = "api/v2"

        # reset URL so the full URL is derived again
        # (primarily allows for switching scheme for WebUI: HTTP <-> HTTPS)
        self._API_BASE_URL = None

        # reset Requests session so it is rebuilt with new auth cookie and all
        self._trigger_session_initialization()

        # reinitialize interaction layers
        self._application = None
        self._authorization = None
        self._transfer = None
        self._torrents = None
        self._torrent_categories = None
        self._torrent_tags = None
        self._log = None
        self._sync = None
        self._rss = None
        self._search = None

    def _initialize_lesser(
        self,
        EXTRA_HEADERS=None,
        REQUESTS_ARGS=None,
        VERIFY_WEBUI_CERTIFICATE=True,
        FORCE_SCHEME_FROM_HOST=False,
        RAISE_UNIMPLEMENTEDERROR_FOR_UNIMPLEMENTED_API_ENDPOINTS=False,
        RAISE_NOTIMPLEMENTEDERROR_FOR_UNIMPLEMENTED_API_ENDPOINTS=False,
        RAISE_ERROR_FOR_UNSUPPORTED_QBITTORRENT_VERSIONS=False,
        VERBOSE_RESPONSE_LOGGING=False,
        PRINT_STACK_FOR_EACH_REQUEST=False,
        SIMPLE_RESPONSES=False,
        DISABLE_LOGGING_DEBUG_OUTPUT=False,
        MOCK_WEB_API_VERSION=None,
    ):
        """Initialize lesser used configuration."""

        # Configuration parameters
        self._EXTRA_HEADERS = EXTRA_HEADERS or {}
        self._REQUESTS_ARGS = REQUESTS_ARGS or {}
        self._VERIFY_WEBUI_CERTIFICATE = bool(VERIFY_WEBUI_CERTIFICATE)
        self._VERBOSE_RESPONSE_LOGGING = bool(VERBOSE_RESPONSE_LOGGING)
        self._PRINT_STACK_FOR_EACH_REQUEST = bool(PRINT_STACK_FOR_EACH_REQUEST)
        self._SIMPLE_RESPONSES = bool(SIMPLE_RESPONSES)
        self._FORCE_SCHEME_FROM_HOST = bool(FORCE_SCHEME_FROM_HOST)
        self._RAISE_UNIMPLEMENTEDERROR_FOR_UNIMPLEMENTED_API_ENDPOINTS = bool(
            RAISE_UNIMPLEMENTEDERROR_FOR_UNIMPLEMENTED_API_ENDPOINTS
            or RAISE_NOTIMPLEMENTEDERROR_FOR_UNIMPLEMENTED_API_ENDPOINTS
        )
        self._RAISE_UNSUPPORTEDVERSIONERROR = bool(
            RAISE_ERROR_FOR_UNSUPPORTED_QBITTORRENT_VERSIONS
        )
        if bool(DISABLE_LOGGING_DEBUG_OUTPUT):
            for logger_ in ("qbittorrentapi", "requests", "urllib3"):
                if getLogger(logger_).level < 20:
                    getLogger(logger_).setLevel("INFO")

        # Environment variables have the lowest priority
        if not self.host:
            env_host = environ.get(
                "QBITTORRENTAPI_HOST", environ.get("PYTHON_QBITTORRENTAPI_HOST")
            )
            if env_host is not None:
                logger.debug(
                    "Using QBITTORRENTAPI_HOST env variable for qBittorrent host"
                )
                self.host = env_host
        if not self.username:
            env_username = environ.get(
                "QBITTORRENTAPI_USERNAME", environ.get("PYTHON_QBITTORRENTAPI_USERNAME")
            )
            if env_username is not None:
                logger.debug("Using QBITTORRENTAPI_USERNAME env variable for username")
                self.username = env_username
        if not self._password:
            env_password = environ.get(
                "QBITTORRENTAPI_PASSWORD", environ.get("PYTHON_QBITTORRENTAPI_PASSWORD")
            )
            if env_password is not None:
                logger.debug("Using QBITTORRENTAPI_PASSWORD env variable for password")
                self._password = env_password
        if self._VERIFY_WEBUI_CERTIFICATE is True:
            env_verify_cert = environ.get(
                "QBITTORRENTAPI_DO_NOT_VERIFY_WEBUI_CERTIFICATE",
                environ.get("PYTHON_QBITTORRENTAPI_DO_NOT_VERIFY_WEBUI_CERTIFICATE"),
            )
            if env_verify_cert is not None:
                self._VERIFY_WEBUI_CERTIFICATE = False

        # Mocking variables until better unit testing exists
        self._MOCK_WEB_API_VERSION = MOCK_WEB_API_VERSION

    @classmethod
    def _list2string(cls, input_list=None, delimiter="|"):
        """
        Convert entries in a list to a concatenated string.

        :param input_list: list to convert
        :param delimiter: delimiter for concatenation
        :return: if input is a list, concatenated string...else whatever the input was
        """
        is_string = isinstance(input_list, six.string_types)
        is_iterable = isinstance(input_list, Iterable)
        if is_iterable and not is_string:
            return delimiter.join(map(str, input_list))
        return input_list

    def _get(
        self,
        _name=APINames.EMPTY,
        _method="",
        requests_args=None,
        requests_params=None,
        headers=None,
        params=None,
        data=None,
        files=None,
        response_class=None,
        **kwargs
    ):
        """
        Send ``GET`` request.

        :param api_namespace: the namespace for the API endpoint
            (e.g. :class:`~qbittorrentapi.definitions.APINames` or ``torrents``)
        :param api_method: the name for the API endpoint (e.g. ``add``)
        :param kwargs: see :meth:`~Request._request`
        :return: Requests :class:`~requests.Response`
        """
        return self._request_manager(
            http_method="get",
            api_namespace=_name,
            api_method=_method,
            requests_args=requests_args,
            requests_params=requests_params,
            headers=headers,
            params=params,
            data=data,
            files=files,
            response_class=response_class,
            **kwargs
        )

    def _post(
        self,
        _name=APINames.EMPTY,
        _method="",
        requests_args=None,
        requests_params=None,
        headers=None,
        params=None,
        data=None,
        files=None,
        response_class=None,
        **kwargs
    ):
        """
        Send ``POST`` request.

        :param api_namespace: the namespace for the API endpoint
            (e.g. :class:`~qbittorrentapi.definitions.APINames` or ``torrents``)
        :param api_method: the name for the API endpoint (e.g. ``add``)
        :param kwargs: see :meth:`~Request._request`
        :return: Requests :class:`~requests.Response`
        """
        return self._request_manager(
            http_method="post",
            api_namespace=_name,
            api_method=_method,
            requests_args=requests_args,
            requests_params=requests_params,
            headers=headers,
            params=params,
            data=data,
            files=files,
            response_class=response_class,
            **kwargs
        )

    def _request_manager(
        self,
        http_method,
        api_namespace,
        api_method,
        _retries=1,
        _retry_backoff_factor=0.3,
        requests_args=None,
        requests_params=None,
        headers=None,
        params=None,
        data=None,
        files=None,
        response_class=None,
        **kwargs
    ):
        """
        Wrapper to manage request retries and severe exceptions.

        This should retry at least once to account for the Web API
        switching from HTTP to HTTPS. During the second attempt, the URL
        is rebuilt using HTTP or HTTPS as appropriate.
        """

        def build_error_msg(exc):
            """Create error message for exception to be raised to user."""
            error_prologue = "Failed to connect to qBittorrent. "
            error_messages = {
                requests_exceptions.SSLError: "This is likely due to using an untrusted certificate "
                "(likely self-signed) for HTTPS qBittorrent WebUI. To suppress this error (and skip "
                "certificate verification consequently exposing the HTTPS connection to man-in-the-middle "
                "attacks), set VERIFY_WEBUI_CERTIFICATE=False when instantiating Client or set "
                "environment variable PYTHON_QBITTORRENTAPI_DO_NOT_VERIFY_WEBUI_CERTIFICATE "
                "to a non-null value. SSL Error: %s" % repr(exc),
                requests_exceptions.HTTPError: "Invalid HTTP Response: %s" % repr(exc),
                requests_exceptions.TooManyRedirects: "Too many redirects: %s"
                % repr(exc),
                requests_exceptions.ConnectionError: "Connection Error: %s" % repr(exc),
                requests_exceptions.Timeout: "Timeout Error: %s" % repr(exc),
                requests_exceptions.RequestException: "Requests Error: %s" % repr(exc),
            }
            err_msg = error_messages.get(type(exc), "Unknown Error: %s" % repr(exc))
            err_msg = error_prologue + err_msg
            logger.debug(err_msg)
            return err_msg

        def retry_backoff(retry_count):
            """
            Back off on attempting each subsequent request retry.

            The first retry is always immediate. if the backoff factor
            is 0.3, then will sleep for 0s then .3s, then .6s, etc.
            between retries.
            """
            if retry_count > 0:
                backoff_time = _retry_backoff_factor * (2 ** ((retry_count + 1) - 1))
                sleep(backoff_time if backoff_time <= 10 else 10)
            logger.debug("Retry attempt %d", retry_count + 1)

        max_retries = _retries if _retries >= 1 else 1
        for retry in range(0, (max_retries + 1)):  # pragma: no branch
            try:
                return self._request(
                    http_method=http_method,
                    api_namespace=api_namespace,
                    api_method=api_method,
                    requests_args=requests_args,
                    requests_params=requests_params,
                    headers=headers,
                    params=params,
                    data=data,
                    files=files,
                    response_class=response_class,
                    **kwargs
                )
            except HTTPError as exc:
                # retry the request for HTTP 500 statuses;
                # raise immediately for other HTTP errors (e.g. 4XX statuses)
                if retry >= max_retries or not isinstance(exc, HTTP5XXError):
                    raise
            except APIError:
                raise
            except Exception as exc:
                if retry >= max_retries:
                    error_message = build_error_msg(exc=exc)
                    response = getattr(exc, "response", None)
                    raise APIConnectionError(error_message, response=response)

            retry_backoff(retry_count=retry)
            self._initialize_context()

    def _request(
        self,
        http_method,
        api_namespace,
        api_method,
        requests_args=None,
        requests_params=None,
        headers=None,
        params=None,
        data=None,
        files=None,
        response_class=None,
        **kwargs
    ):
        """
        Meat and potatoes of sending requests to qBittorrent.

        :param http_method: ``get`` or ``post``
        :param api_namespace: the namespace for the API endpoint
            (e.g. :class:`~qbittorrentapi.definitions.APINames` or ``torrents``)
        :param api_method: the name for the API endpoint (e.g. ``add``)
        :param requests_args: default location for Requests kwargs
        :param requests_params: alternative location for Requests kwargs
        :param headers: HTTP headers to send with the request
        :param params: key/value pairs to send with a ``GET`` request
        :param data: key/value pairs to send with a ``POST`` request
        :param files: files to be sent with the request
        :param response_class: class to use to cast the API response
        :param kwargs: arbitrary keyword arguments to send with the request
        :return: Requests :class:`~requests.Response`
        """
        response_kwargs, kwargs = self._get_response_kwargs(kwargs)
        requests_kwargs = self._get_requests_kwargs(requests_args, requests_params)
        headers = self._get_headers(headers, requests_kwargs.pop("headers", {}))
        url = self._url.build_url(api_namespace, api_method, headers, requests_kwargs)
        params, data, files = self._get_data(http_method, params, data, files, **kwargs)

        response = self._session.request(
            http_method,
            url,
            params=params,
            data=data,
            files=files,
            headers=headers,
            **requests_kwargs
        )

        self._verbose_logging(http_method, url, data, params, requests_kwargs, response)
        self._handle_error_responses(data, params, response)
        return self._cast(response, response_class, **response_kwargs)

    @staticmethod
    def _get_response_kwargs(kwargs):
        """
        Determine the kwargs for managing the response to return.

        :param kwargs: extra keywords arguments to be passed along in request
        :return: sanitized arguments
        """
        response_kwargs = {
            "SIMPLE_RESPONSES": kwargs.pop(
                "SIMPLE_RESPONSES", kwargs.pop("SIMPLE_RESPONSE", None)
            )
        }
        return response_kwargs, kwargs

    def _get_requests_kwargs(self, requests_args=None, requests_params=None):
        """
        Determine the requests_kwargs for the call to Requests. The global
        configuration in ``self._REQUESTS_ARGS`` is updated by any arguments
        provided for a specific call.

        :param requests_args: default location to expect Requests ``requests_kwargs``
        :param requests_params: alternative location to expect Requests ``requests_kwargs``
        :return: final dictionary of Requests ``requests_kwargs``
        """
        requests_kwargs = deepcopy(self._REQUESTS_ARGS)
        requests_kwargs.update(requests_args or requests_params or {})
        return requests_kwargs

    @staticmethod
    def _get_headers(headers=None, more_headers=None):
        """
        Determine headers specific to this request. Request headers can be
        specified explicitly or with the requests kwargs. Headers specified in
        ``self._EXTRA_HEADERS`` are merged in Requests itself.

        :param headers: headers specified for this specific request
        :param more_headers: headers from requests_kwargs arguments
        :return: final dictionary of headers for this specific request
        """
        user_headers = more_headers or {}
        user_headers.update(headers or {})
        return user_headers

    @staticmethod
    def _get_data(http_method, params=None, data=None, files=None, **kwargs):
        """
        Determine ``data``, ``params``, and ``files`` for the Requests call.

        :param http_method: ``get`` or ``post``
        :param params: key value pairs to send with GET calls
        :param data: key value pairs to send with POST calls
        :param files: dictionary of files to send with request
        :return: final dictionaries of data to send to qBittorrent
        """
        params = params or {}
        data = data or {}
        files = files or {}

        # any other keyword arguments are sent to qBittorrent as part of the request.
        # These are user-defined since this Client will put everything in data/params/files
        # that needs to be sent to qBittorrent.
        if kwargs:
            if http_method == "get":
                params.update(kwargs)
            if http_method == "post":
                data.update(kwargs)

        return params, data, files

    def _cast(self, response, response_class, **response_kwargs):
        """
        Returns the API response casted to the requested class.

        :param response: requests ``Response`` from API
        :param response_class: class to return response as; if none, response is returned
        :param response_kwargs: request-specific configuration for response
        :return: API response as type of ``response_class``
        """
        try:
            if response_class is None:
                return response
            if response_class is six.text_type:
                # convert back to bytes for python 2 since it's always worked that way...
                return str(response.text)
            if response_class is int:
                return int(response.text)
            if response_class is bytes:
                return response.content
            if issubclass(response_class, (Dictionary, List)):
                try:
                    result = response.json()
                except AttributeError:
                    # just in case the requests package is old and doesn't contain json()
                    result = loads(response.text)
                if self._SIMPLE_RESPONSES or response_kwargs.get("SIMPLE_RESPONSES"):
                    return result
                else:
                    return response_class(result, client=self)
        except Exception as exc:
            logger.debug("Exception during response parsing.", exc_info=True)
            raise APIError("Exception during response parsing. Error: %r" % exc)
        else:
            logger.debug("No handler defined to cast response.", exc_info=True)
            raise APIError("No handler defined to cast response to %r" % response_class)

    @property
    def _session(self):
        """
        Create or return existing HTTP session.

        :return: Requests :class:`~requests.Session` object
        """

        class QbittorrentSession(Session):
            """
            Wrapper to augment Requests Session.

            Requests doesn't allow Session to default certain
            configuration globally. This gets around that by setting
            defaults for each request.
            """

            def request(self, method, url, **kwargs):
                kwargs.setdefault("timeout", 15.1)
                kwargs.setdefault("allow_redirects", True)

                # send Content-Length as 0 for empty POSTs...Requests will not send Content-Length
                # if data is empty but qBittorrent will complain otherwise
                is_data = any(x is not None for x in kwargs.get("data", {}).values())
                if method.lower() == "post" and not is_data:
                    kwargs.setdefault("headers", {}).update({"Content-Length": "0"})

                return super(QbittorrentSession, self).request(method, url, **kwargs)

        if self._http_session:
            return self._http_session

        self._http_session = QbittorrentSession()

        # add any user-defined headers to be sent in all requests
        self._http_session.headers.update(self._EXTRA_HEADERS)

        # enable/disable TLS verification for all requests
        self._http_session.verify = self._VERIFY_WEBUI_CERTIFICATE

        # enable retries in Requests if HTTP call fails.
        # this is sorta doubling up on retries since request_manager() will
        # attempt retries as well. however, these retries will not delay.
        # so, if the problem is just a network blip then Requests will
        # automatically retry (with zero delay) and probably fix the issue
        # without coming all the way back to requests_wrapper. if this retries
        # is increased much above 1, and backoff_factor is non-zero, this
        # will start adding noticeable delays in these retry attempts...which
        # would then compound with similar delay logic in request_manager.
        # at any rate, the retries count in request_manager should always be
        # at least 2 to accommodate significant settings changes in qBittorrent
        # such as enabling HTTPs in Web UI settings.
        adapter = HTTPAdapter(
            max_retries=Retry(
                total=1,
                read=1,
                connect=1,
                status_forcelist={500, 502, 504},
                raise_on_status=False,
            )
        )
        self._http_session.mount("http://", adapter)
        self._http_session.mount("https://", adapter)

        return self._http_session

    def __del__(self):
        """
        Close HTTP Session before destruction.

        This isn't strictly necessary since this will automatically
        happen when the Session is garbage collected...but it makes
        Python's ResourceWarning logging for unclosed sockets cleaner.
        """
        self._trigger_session_initialization()

    def _trigger_session_initialization(self):
        """
        Effectively resets the HTTP session by removing the reference to it.

        During the next request, a new session will be created.
        """
        try:
            self._http_session.close()
        except AttributeError:
            pass
        self._http_session = None

    @staticmethod
    def _handle_error_responses(data, params, response):
        """Raise proper exception if qBittorrent returns Error HTTP Status."""
        if response.status_code < 400:
            # short circuit for non-error statuses
            return

        if response.status_code == 400:
            # Returned for malformed requests such as missing or invalid parameters.
            # If an error_message isn't returned, qBittorrent didn't receive all required parameters.
            # APIErrorType::BadParams
            # the name of the HTTP error (i.e. Bad Request) started being returned in v4.3.0
            if response.text in ("", "Bad Request"):
                raise MissingRequiredParameters400Error()
            raise InvalidRequest400Error(response.text)

        if response.status_code == 401:
            # Primarily reserved for XSS and host header issues.
            raise Unauthorized401Error(response.text)

        if response.status_code == 403:
            # Not logged in or calling an API method that isn't public
            # APIErrorType::AccessDenied
            raise Forbidden403Error(response.text)

        if response.status_code == 404:
            # API method doesn't exist or more likely, torrent not found
            # APIErrorType::NotFound
            error_message = response.text
            if error_message in ("", "Not Found"):
                hash_source = data or params or {}
                error_hash = hash_source.get("hashes", hash_source.get("hash", ""))
                if error_hash:
                    error_message = "Torrent hash(es): %s" % error_hash
            raise NotFound404Error(error_message)

        if response.status_code == 405:
            # HTTP method not allowed for the API endpoint.
            # This should only be raised if qBittorrent changes the requirement for an endpoint...
            raise MethodNotAllowed405Error(response.text)

        if response.status_code == 409:
            # APIErrorType::Conflict
            raise Conflict409Error(response.text)

        if response.status_code == 415:
            # APIErrorType::BadData
            raise UnsupportedMediaType415Error(response.text)

        if response.status_code >= 500:
            http_error = InternalServerError500Error(response.text)
            http_error.http_status_code = response.status_code
            raise http_error

        # Unaccounted for API errors
        http_error = HTTPError(response.text)
        http_error.http_status_code = response.status_code
        raise http_error

    def _verbose_logging(
        self, http_method, url, data, params, requests_kwargs, response
    ):
        """
        Log verbose information about request.

        Can be useful during development.
        """
        if self._VERBOSE_RESPONSE_LOGGING:
            resp_logger = logger.debug
            max_text_length_to_log = 254
            if response.status_code != 200:
                # log as much as possible in an error condition
                max_text_length_to_log = 10000

            resp_logger("Request URL: (%s) %s", http_method.upper(), response.url)
            resp_logger("Request Headers: %s", response.request.headers)
            resp_logger("Request HTTP Data: %s", {"data": data, "params": params})
            resp_logger("Requests Config: %s", requests_kwargs)
            if (
                str(response.request.body) not in ("None", "")
                and "auth/login" not in url
            ):
                body_len = (
                    max_text_length_to_log
                    if len(response.request.body) > max_text_length_to_log
                    else len(response.request.body)
                )
                resp_logger(
                    "Request body: %s%s",
                    response.request.body[:body_len],
                    "...<truncated>" if body_len >= 200 else "",
                )

            resp_logger(
                "Response status: %s (%s)", response.status_code, response.reason
            )
            if response.text:
                text_len = (
                    max_text_length_to_log
                    if len(response.text) > max_text_length_to_log
                    else len(response.text)
                )
                resp_logger(
                    "Response text: %s%s",
                    response.text[:text_len],
                    "...<truncated>" if text_len >= 80 else "",
                )
        if self._PRINT_STACK_FOR_EACH_REQUEST:
            from traceback import print_stack

            print_stack()
