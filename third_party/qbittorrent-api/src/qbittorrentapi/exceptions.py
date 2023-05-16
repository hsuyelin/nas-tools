from requests.exceptions import HTTPError as RequestsHTTPError
from requests.exceptions import RequestException


class APIError(Exception):
    """Base error for all exceptions from this Client."""


class UnsupportedQbittorrentVersion(APIError):
    """Connected qBittorrent is not fully supported by this Client."""


class FileError(IOError, APIError):
    """Base class for all exceptions for file handling."""


class TorrentFileError(FileError):
    """Base class for all exceptions for torrent files."""


class TorrentFileNotFoundError(TorrentFileError):
    """Specified torrent file does not appear to exist."""


class TorrentFilePermissionError(TorrentFileError):
    """Permission was denied to read the specified torrent file."""


class APIConnectionError(RequestException, APIError):
    """Base class for all communications errors including HTTP errors."""


class LoginFailed(APIConnectionError):
    """This can technically be raised with any request since log in may be
    attempted for any request and could fail."""


class HTTPError(RequestsHTTPError, APIConnectionError):
    """
    Base error for all HTTP errors.

    All errors following a successful connection to qBittorrent are
    returned as HTTP statuses.
    """

    http_status_code = None


class HTTP4XXError(HTTPError):
    """Base error for all HTTP 4XX statuses."""


class HTTP5XXError(HTTPError):
    """Base error for all HTTP 5XX statuses."""


class HTTP400Error(HTTP4XXError):
    """HTTP 400 Status."""

    http_status_code = 400


class HTTP401Error(HTTP4XXError):
    """HTTP 401 Status."""

    http_status_code = 401


class HTTP403Error(HTTP4XXError):
    """HTTP 403 Status."""

    http_status_code = 403


class HTTP404Error(HTTP4XXError):
    """HTTP 404 Status."""

    http_status_code = 404


class HTTP405Error(HTTP4XXError):
    """HTTP 405 Status."""

    http_status_code = 405


class HTTP409Error(HTTP4XXError):
    """HTTP 409 Status."""

    http_status_code = 409


class HTTP415Error(HTTP4XXError):
    """HTTP 415 Status."""

    http_status_code = 415


class HTTP500Error(HTTP5XXError):
    """HTTP 500 Status."""

    http_status_code = 500


class MissingRequiredParameters400Error(HTTP400Error):
    """Endpoint call is missing one or more required parameters."""


class InvalidRequest400Error(HTTP400Error):
    """One or more endpoint arguments are malformed."""


class Unauthorized401Error(HTTP401Error):
    """Primarily reserved for XSS and host header issues."""


class Forbidden403Error(HTTP403Error):
    """Not logged in, IP has been banned, or calling an API method that isn't
    public."""


class NotFound404Error(HTTP404Error):
    """This should mean qBittorrent couldn't find a torrent for the torrent
    hash."""


class MethodNotAllowed405Error(HTTP405Error):
    """HTTP method is not supported for the API endpoint."""


class Conflict409Error(HTTP409Error):
    """Returned if arguments don't make sense specific to the endpoint."""


class UnsupportedMediaType415Error(HTTP415Error):
    """``torrents/add`` endpoint will return this for invalid URL(s) or
    files."""


class InternalServerError500Error(HTTP500Error):
    """Returned if qBittorrent errors internally while processing the
    request."""
