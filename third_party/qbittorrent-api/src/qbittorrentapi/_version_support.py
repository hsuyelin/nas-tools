from pkg_resources import parse_version

try:
    from functools import lru_cache
except ImportError:  # pragma: no cover
    from backports.functools_lru_cache import lru_cache


APP_VERSION_2_API_VERSION_MAP = {
    "v4.1.0": "2.0",
    "v4.1.1": "2.0.1",
    "v4.1.2": "2.0.2",
    "v4.1.3": "2.1",
    "v4.1.4": "2.1.1",
    "v4.1.5": "2.2",
    "v4.1.6": "2.2",
    "v4.1.7": "2.2",
    "v4.1.8": "2.2",
    "v4.1.9": "2.2.1",
    "v4.1.9.1": "2.2.1",
    "v4.2.0": "2.3",
    "v4.2.1": "2.4",
    "v4.2.2": "2.4.1",
    "v4.2.3": "2.4.1",
    "v4.2.4": "2.5",
    "v4.2.5": "2.5.1",
    "v4.3.0": "2.6",
    "v4.3.0.1": "2.6",
    "v4.3.1": "2.6.1",
    "v4.3.2": "2.7",
    "v4.3.3": "2.7",
    "v4.3.4.1": "2.8.1",
    "v4.3.5": "2.8.2",
    "v4.3.6": "2.8.2",
    "v4.3.7": "2.8.2",
    "v4.3.8": "2.8.2",
    "v4.3.9": "2.8.2",
    "v4.4.0": "2.8.4",
    "v4.4.1": "2.8.5",
    "v4.4.2": "2.8.5",
    "v4.4.3": "2.8.5",
    "v4.4.3.1": "2.8.5",
    "v4.4.4": "2.8.5",
    "v4.4.5": "2.8.5",
    "v4.5.0beta1": "2.8.14",
    "v4.5.0": "2.8.18",
    "v4.5.1": "2.8.19",
    "v4.5.2": "2.8.19",
}

MOST_RECENT_SUPPORTED_APP_VERSION = "v4.5.2"
MOST_RECENT_SUPPORTED_API_VERSION = "2.8.19"


@lru_cache(maxsize=None)
def v(version):
    """Caching version parser."""
    return parse_version(version)


class Version(object):
    """
    Allows introspection for whether this Client supports different versions of
    the qBittorrent application and its Web API.

    Note that if a version is not listed as "supported" here, many (if
    not all) methods are likely to function properly since the Web API
    is largely backwards and forward compatible...albeit with some
    notable exceptions.
    """

    _supported_app_versions = None
    _supported_api_versions = None

    @classmethod
    def supported_app_versions(cls):
        """Set of all supported qBittorrent application versions."""
        if cls._supported_app_versions is None:
            cls._supported_app_versions = set(APP_VERSION_2_API_VERSION_MAP.keys())
        return cls._supported_app_versions

    @classmethod
    def supported_api_versions(cls):
        """Set of all supported qBittorrent Web API versions."""
        if cls._supported_api_versions is None:
            cls._supported_api_versions = set(APP_VERSION_2_API_VERSION_MAP.values())
        return cls._supported_api_versions

    @classmethod
    def is_app_version_supported(cls, app_version):
        """
        Returns whether a version of the qBittorrent application is fully
        supported by this API client.

        :param app_version: version of qBittorrent application such as v4.4.0
        :return: ``True`` or ``False`` for whether version is supported
        """
        app_version = app_version.lower()
        if not app_version.startswith("v"):
            app_version = "v" + app_version
        return app_version in cls.supported_app_versions()

    @classmethod
    def is_api_version_supported(cls, api_version):
        """
        Returns whether a version of the qBittorrent Web API is fully supported
        by this API client.

        :param api_version: version of qBittorrent Web API version such as ``2.8.4``
        :return: ``True`` or ``False`` for whether version is supported
        """
        api_version = api_version.lower()
        if api_version.startswith("v"):
            api_version = api_version[1:]
        return api_version in Version.supported_api_versions()

    @classmethod
    def latest_supported_app_version(cls):
        """Returns the most recent version of qBittorrent application that is
        fully supported."""
        return MOST_RECENT_SUPPORTED_APP_VERSION

    @classmethod
    def latest_supported_api_version(cls):
        """Returns the most recent version of qBittorrent Web API that is fully
        supported."""
        return MOST_RECENT_SUPPORTED_API_VERSION
