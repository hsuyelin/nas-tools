from logging import getLogger

from qbittorrentapi import Version
from qbittorrentapi.decorators import login_required
from qbittorrentapi.definitions import APINames
from qbittorrentapi.definitions import ClientCache
from qbittorrentapi.exceptions import HTTP403Error
from qbittorrentapi.exceptions import LoginFailed
from qbittorrentapi.exceptions import UnsupportedQbittorrentVersion
from qbittorrentapi.request import Request

logger = getLogger(__name__)


class Authorization(ClientCache):
    """
    Allows interaction with the ``Authorization`` API endpoints.

    :Usage:
        >>> from qbittorrentapi import Client
        >>> client = Client(host='localhost:8080', username='admin', password='adminadmin')
        >>> is_logged_in = client.auth.is_logged_in
        >>> client.auth.log_in(username='admin', password='adminadmin')
        >>> client.auth.log_out()
    """

    @property
    def is_logged_in(self):
        """Implements :meth:`~AuthAPIMixIn.is_logged_in`"""
        return self._client.is_logged_in

    def log_in(self, username=None, password=None, **kwargs):
        """Implements :meth:`~AuthAPIMixIn.auth_log_in`"""
        return self._client.auth_log_in(username=username, password=password, **kwargs)

    def log_out(self, **kwargs):
        """Implements :meth:`~AuthAPIMixIn.auth_log_out`"""
        return self._client.auth_log_out(**kwargs)


class AuthAPIMixIn(Request):
    """
    Implementation of all ``Authorization`` API methods.

    :Usage:
        >>> from qbittorrentapi import Client
        >>> client = Client(host='localhost:8080', username='admin', password='adminadmin')
        >>> _ = client.is_logged_in
        >>> client.auth_log_in(username='admin', password='adminadmin')
        >>> client.auth_log_out()
    """

    @property
    def auth(self):
        """
        Allows for transparent interaction with Authorization endpoints.

        :return: Auth object
        """
        if self._authorization is None:
            self._authorization = Authorization(client=self)
        return self._authorization

    authorization = auth

    @property
    def is_logged_in(self):
        """
        Returns True if low-overhead API call succeeds; False otherwise.

        There isn't a reliable way to know if an existing session is still valid
        without attempting to use it. qBittorrent invalidates cookies when they expire.

        :returns: True/False if current auth cookie is accepted by qBittorrent.
        """
        try:
            self._post(_name=APINames.Application, _method="version")
        except HTTP403Error:
            return False
        else:
            return True

    def auth_log_in(self, username=None, password=None, **kwargs):
        """
        Log in to qBittorrent host.

        :raises LoginFailed: if credentials failed to log in
        :raises Forbidden403Error: if user is banned...or not logged in

        :param username: username for qBittorrent client
        :param password: password for qBittorrent client
        :return: None
        """
        if username:
            self.username = username
            self._password = password or ""

        self._initialize_context()
        creds = {"username": self.username, "password": self._password}
        auth_response = self._post(
            _name=APINames.Authorization, _method="login", data=creds, **kwargs
        )

        if auth_response.text != "Ok.":
            logger.debug("Login failed")
            raise LoginFailed()
        logger.debug("Login successful")

        # check if the connected qBittorrent is fully supported by this Client yet
        if self._RAISE_UNSUPPORTEDVERSIONERROR:
            app_version = self.app_version()
            api_version = self.app_web_api_version()
            if not (
                Version.is_api_version_supported(api_version)
                and Version.is_app_version_supported(app_version)
            ):
                raise UnsupportedQbittorrentVersion(
                    "This version of qBittorrent is not fully supported => App Version: %s API Version: %s"
                    % (app_version, api_version)
                )

    @property
    def _SID(self):
        """
        Authorization session cookie from qBittorrent using default cookie name
        `SID`. Backwards compatible for :meth:`~AuthAPIMixIn._session_cookie`.

        :return: Auth cookie value from qBittorrent or None if one isn't already acquired
        """
        return self._session_cookie()

    def _session_cookie(self, cookie_name="SID"):
        """
        Authorization session cookie from qBittorrent.

        :param cookie_name: Name of the authorization cookie; configurable after v4.5.0.
        :return: Auth cookie value from qBittorrent or None if one isn't already acquired
        """
        if self._http_session:
            return self._http_session.cookies.get(cookie_name, None)
        return None

    @login_required
    def auth_log_out(self, **kwargs):
        """End session with qBittorrent."""
        self._post(_name=APINames.Authorization, _method="logout", **kwargs)
